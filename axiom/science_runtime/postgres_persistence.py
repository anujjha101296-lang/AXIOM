"""Durable SQL persistence for bounded scientific research runs.

The adapter mirrors the small ResearchRunStore contract used by the API while
moving lifecycle state into a transactional relational database. PostgreSQL is
the production target; SQLite remains useful for contract tests.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .research_loop import ResearchRun, Transition


class _Base(DeclarativeBase):
    pass


class ResearchRunRow(_Base):
    __tablename__ = "research_runs"

    run_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ResearchSubmissionRow(_Base):
    __tablename__ = "research_submissions"

    idempotency_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    run_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="QUEUED")
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ResearchEventRow(_Base):
    __tablename__ = "research_events"

    run_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class PostgresResearchRunStore:
    """Transactional durable store implementing the research event/snapshot boundary."""

    def __init__(self, database_url: str, *, create_schema: bool = False) -> None:
        normalized = database_url
        if normalized.startswith("postgresql://"):
            normalized = normalized.replace("postgresql://", "postgresql+psycopg://", 1)
        self.engine = create_engine(normalized, future=True, pool_pre_ping=True)
        if create_schema:
            _Base.metadata.create_all(self.engine)

    @property
    def backend_name(self) -> str:
        return "postgresql"

    def check_ready(self) -> None:
        """Fail closed if the durable database cannot be reached."""
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    @staticmethod
    def _lock_run(session: Session, run_id: str) -> None:
        """Serialize event sequence allocation for one run on PostgreSQL."""
        if session.bind is not None and session.bind.dialect.name == "postgresql":
            session.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:run_id))"),
                {"run_id": run_id},
            )

    @staticmethod
    def _lock_submission(session: Session, idempotency_key: str) -> None:
        """Serialize concurrent reservations for one idempotency key on PostgreSQL."""
        if session.bind is not None and session.bind.dialect.name == "postgresql":
            session.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:idempotency_key))"),
                {"idempotency_key": idempotency_key},
            )

    def _ensure_run(self, session: Session, run: ResearchRun, now: datetime) -> ResearchRunRow:
        row = session.get(ResearchRunRow, run.run_id, with_for_update=True)
        if row is None:
            row = ResearchRunRow(
                run_id=run.run_id,
                snapshot=asdict(run),
                updated_at=now,
            )
            session.add(row)
            session.flush()
        return row

    def _append_locked(
        self,
        session: Session,
        run: ResearchRun,
        event_type: str,
        payload: dict[str, Any],
        now: datetime,
    ) -> ResearchEventRow:
        self._lock_run(session, run.run_id)
        row = self._ensure_run(session, run, now)
        last = session.execute(
            select(ResearchEventRow.sequence)
            .where(ResearchEventRow.run_id == run.run_id)
            .order_by(ResearchEventRow.sequence.desc())
            .limit(1)
            .with_for_update()
        ).scalar_one_or_none()
        sequence = int(last or 0) + 1
        event = ResearchEventRow(
            run_id=run.run_id,
            sequence=sequence,
            event_id=f"{run.run_id}:{sequence}",
            event_type=event_type,
            stage=run.stage.value,
            timestamp=now,
            payload=payload,
        )
        session.add(event)
        row.snapshot = asdict(run)
        row.updated_at = now
        session.flush()
        return event

    def reserve_submission(self, idempotency_key: str, request_fingerprint: str, run_id: str) -> tuple[str, bool]:
        """Atomically reserve an idempotent submission or return its existing run."""
        now = datetime.now(timezone.utc)
        with Session(self.engine, expire_on_commit=False) as session, session.begin():
            self._lock_submission(session, idempotency_key)
            row = session.get(ResearchSubmissionRow, idempotency_key, with_for_update=True)
            if row is not None:
                if row.request_fingerprint != request_fingerprint:
                    raise ValueError("Idempotency key was already used for a different research request")
                return row.run_id, False
            session.add(
                ResearchSubmissionRow(
                    idempotency_key=idempotency_key,
                    request_fingerprint=request_fingerprint,
                    run_id=run_id,
                    created_at=now,
                )
            )
            return run_id, True

    def reserve_submission_and_initialize(
        self,
        idempotency_key: str,
        request_fingerprint: str,
        run: ResearchRun,
        transition: Transition,
    ) -> tuple[str, bool]:
        """Reserve a submission and persist its initial run state in one transaction.

        A successful reservation can never commit without the corresponding
        research run/event. This prevents a client retry from resolving to a
        run_id whose initial state was never durably created.
        """
        now = datetime.now(timezone.utc)
        payload = {"detail": transition.detail, "transition_stage": transition.stage}
        with Session(self.engine, expire_on_commit=False) as session, session.begin():
            self._lock_submission(session, idempotency_key)
            existing = session.get(ResearchSubmissionRow, idempotency_key, with_for_update=True)
            if existing is not None:
                if existing.request_fingerprint != request_fingerprint:
                    raise ValueError("Idempotency key was already used for a different research request")
                return existing.run_id, False

            session.add(
                ResearchSubmissionRow(
                    idempotency_key=idempotency_key,
                    request_fingerprint=request_fingerprint,
                    run_id=run.run_id,
                    created_at=now,
                    status="QUEUED",
                    heartbeat_at=now,
                )
            )
            self._append_locked(session, run, transition.action.upper(), payload, now)
            return run.run_id, True

    def mark_submission_running(self, run_id: str) -> None:
        now = datetime.now(timezone.utc)
        with Session(self.engine) as session, session.begin():
            row = session.execute(
                select(ResearchSubmissionRow)
                .where(ResearchSubmissionRow.run_id == run_id)
                .with_for_update()
            ).scalar_one_or_none()
            if row is not None:
                row.status = "RUNNING"
                row.heartbeat_at = now

    def heartbeat_submission(self, run_id: str) -> None:
        now = datetime.now(timezone.utc)
        with Session(self.engine) as session, session.begin():
            row = session.execute(
                select(ResearchSubmissionRow)
                .where(ResearchSubmissionRow.run_id == run_id)
                .with_for_update()
            ).scalar_one_or_none()
            if row is not None:
                row.heartbeat_at = now

    def mark_submission_terminal(self, run_id: str, status: str) -> None:
        if status not in {"COMPLETED", "FAILED"}:
            raise ValueError("Terminal submission status must be COMPLETED or FAILED")
        now = datetime.now(timezone.utc)
        with Session(self.engine) as session, session.begin():
            row = session.execute(
                select(ResearchSubmissionRow)
                .where(ResearchSubmissionRow.run_id == run_id)
                .with_for_update()
            ).scalar_one_or_none()
            if row is not None:
                row.status = status
                row.heartbeat_at = now

    def claim_stale_submission(self, run_id: str, stale_after_seconds: int = 60) -> bool:
        now = datetime.now(timezone.utc)
        with Session(self.engine) as session, session.begin():
            row = session.execute(
                select(ResearchSubmissionRow)
                .where(ResearchSubmissionRow.run_id == run_id)
                .with_for_update()
            ).scalar_one_or_none()
            if row is None or row.status in {"COMPLETED", "FAILED"}:
                return False
            heartbeat = row.heartbeat_at
            if heartbeat.tzinfo is None:
                heartbeat = heartbeat.replace(tzinfo=timezone.utc)
            if row.status == "RUNNING" and (now - heartbeat).total_seconds() < stale_after_seconds:
                return False
            row.status = "RUNNING"
            row.heartbeat_at = now
            return True

    def submission_status(self, run_id: str) -> tuple[str, datetime] | None:
        with Session(self.engine) as session:
            row = session.execute(
                select(ResearchSubmissionRow.status, ResearchSubmissionRow.heartbeat_at)
                .where(ResearchSubmissionRow.run_id == run_id)
            ).one_or_none()
            return None if row is None else (str(row.status), row.heartbeat_at)

    def append(self, run: ResearchRun, event_type: str, payload: dict[str, Any] | None = None) -> ResearchEventRow:
        now = datetime.now(timezone.utc)
        with Session(self.engine, expire_on_commit=False) as session, session.begin():
            return self._append_locked(session, run, event_type, payload or {}, now)

    def record_transition(self, run: ResearchRun, transition: Transition) -> ResearchEventRow:
        return self.append(
            run,
            transition.action.upper(),
            {"detail": transition.detail, "transition_stage": transition.stage},
        )

    def snapshot(self, run: ResearchRun) -> None:
        now = datetime.now(timezone.utc)
        with Session(self.engine) as session, session.begin():
            row = session.get(ResearchRunRow, run.run_id, with_for_update=True)
            if row is None:
                session.add(ResearchRunRow(run_id=run.run_id, snapshot=asdict(run), updated_at=now))
            else:
                row.snapshot = asdict(run)
                row.updated_at = now

    def persist_transition(self, run: ResearchRun, transition: Transition) -> ResearchEventRow:
        """Persist one lifecycle event and its corresponding snapshot atomically."""
        now = datetime.now(timezone.utc)
        payload = {"detail": transition.detail, "transition_stage": transition.stage}
        with Session(self.engine, expire_on_commit=False) as session, session.begin():
            return self._append_locked(session, run, transition.action.upper(), payload, now)

    def read_events(self, run_id: str, after_sequence: int = 0) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            rows = session.execute(
                select(ResearchEventRow)
                .where(
                    ResearchEventRow.run_id == run_id,
                    ResearchEventRow.sequence > after_sequence,
                )
                .order_by(ResearchEventRow.sequence)
            ).scalars()
            return [
                {
                    "schema_version": "axiom.research.event.v1",
                    "event_id": row.event_id,
                    "sequence": row.sequence,
                    "run_id": row.run_id,
                    "event_type": row.event_type,
                    "timestamp": row.timestamp.isoformat(),
                    "stage": row.stage,
                    "payload": row.payload,
                }
                for row in rows
            ]

    def read_snapshot(self, run_id: str) -> dict[str, Any] | None:
        with Session(self.engine) as session:
            row = session.get(ResearchRunRow, run_id)
            return None if row is None else row.snapshot

    def close(self) -> None:
        self.engine.dispose()


__all__ = ["PostgresResearchRunStore", "ResearchEventRow", "ResearchRunRow", "ResearchSubmissionRow"]

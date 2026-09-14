"""Durable SQL persistence for bounded scientific research runs.

The adapter mirrors the small ResearchRunStore contract used by the API while
moving lifecycle state into a transactional relational database. PostgreSQL is
the production target; SQLite remains useful for contract tests.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .research_loop import ResearchRun, Transition


class _Base(DeclarativeBase):
    pass


class ResearchRunRow(_Base):
    __tablename__ = "research_runs"

    run_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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

    def append(self, run: ResearchRun, event_type: str, payload: dict[str, Any] | None = None) -> ResearchEventRow:
        now = datetime.now(timezone.utc)
        with Session(self.engine) as session, session.begin():
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
                payload=payload or {},
            )
            session.add(event)
            return event

    def record_transition(self, run: ResearchRun, transition: Transition) -> ResearchEventRow:
        return self.append(
            run,
            transition.action.upper(),
            {"detail": transition.detail, "transition_stage": transition.stage},
        )

    def snapshot(self, run: ResearchRun) -> None:
        now = datetime.now(timezone.utc)
        payload = asdict(run)
        with Session(self.engine) as session, session.begin():
            row = session.get(ResearchRunRow, run.run_id, with_for_update=True)
            if row is None:
                session.add(ResearchRunRow(run_id=run.run_id, snapshot=payload, updated_at=now))
            else:
                row.snapshot = payload
                row.updated_at = now

    def persist_transition(self, run: ResearchRun, transition: Transition) -> ResearchEventRow:
        """Persist event and snapshot in one transaction."""
        now = datetime.now(timezone.utc)
        payload = {"detail": transition.detail, "transition_stage": transition.stage}
        with Session(self.engine) as session, session.begin():
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
                event_type=transition.action.upper(),
                stage=run.stage.value,
                timestamp=now,
                payload=payload,
            )
            session.add(event)
            snapshot = asdict(run)
            row = session.get(ResearchRunRow, run.run_id, with_for_update=True)
            if row is None:
                session.add(ResearchRunRow(run_id=run.run_id, snapshot=snapshot, updated_at=now))
            else:
                row.snapshot = snapshot
                row.updated_at = now
            return event

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


__all__ = ["PostgresResearchRunStore", "ResearchEventRow", "ResearchRunRow"]

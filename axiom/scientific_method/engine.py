"""Scientific Method Engine — orchestrates the mandatory 10-phase research workflow."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from axiom.observability.run_provenance import capture_environment, get_provenance_store
from axiom.scientific_method.models import (
    PHASE_ORDER,
    ProblemDefinition,
    SMEPhase,
    SMESession,
    SMESessionStatus,
)
from axiom.scientific_method.phases import PhaseExecutor
from axiom.scientific_method.store import SMEStore


class SMEPhaseIncompleteError(Exception):
    """Raised when attempting to advance without completing the current phase."""


class SMEBypassError(Exception):
    """Raised when a research workflow attempts to bypass the Scientific Method Engine."""


# Domains where SME is mandatory for autonomous research
SME_MANDATORY_DOMAINS = frozenset({
    "research", "mathematics", "math", "science", "general", "engineering",
})


class ScientificMethodEngine:
    """
    Governs every autonomous research task through 10 disciplined phases.
    No research workflow may bypass this engine.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = SMEStore(db_path)
        self.executor = PhaseExecutor(db_path)

    def create_session(
        self,
        objective: str,
        domain: str = "research",
        problem: ProblemDefinition | None = None,
        workflow_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SMESession:
        """Start a new SME-governed research session."""
        session = SMESession(
            objective=objective,
            domain=domain,
            problem=problem,
            workflow_id=workflow_id,
            status=SMESessionStatus.IN_PROGRESS,
            metadata=metadata or {},
        )
        self.store.save_session(session)
        return session

    def get_session(self, session_id: str) -> SMESession | None:
        return self.store.get_session(session_id)

    def execute_phase(self, session_id: str, phase: SMEPhase | None = None) -> SMESession:
        """Execute a single phase. Defaults to current_phase."""
        session = self._load(session_id)
        target = phase or session.current_phase

        if target in session.phases_completed:
            raise SMEPhaseIncompleteError(f"Phase {target.value} already completed.")

        idx = PHASE_ORDER.index(target)
        if idx > 0 and PHASE_ORDER[idx - 1] not in session.phases_completed:
            raise SMEPhaseIncompleteError(
                f"Cannot execute {target.value}: prior phase {PHASE_ORDER[idx - 1].value} not completed."
            )

        result = self.executor.execute(session, target)
        session.phase_results.append(result)

        if not result.completed:
            session.status = SMESessionStatus.FAILED
            self.store.save_session(session)
            raise SMEPhaseIncompleteError(
                f"Phase {target.value} failed: {'; '.join(result.errors)}"
            )

        session.phases_completed.append(target)
        next_idx = idx + 1
        if next_idx < len(PHASE_ORDER):
            session.current_phase = PHASE_ORDER[next_idx]
        else:
            session.status = SMESessionStatus.COMPLETED
            session.current_phase = target
            self._record_provenance(session)

        session.updated_at = datetime.now(timezone.utc)
        self.store.save_session(session)

        if target == SMEPhase.RESEARCH_MEMORY:
            for record in session.memory_records:
                self.store.save_memory_record(
                    session.session_id,
                    record.model_dump(mode="json"),
                )

        return session

    def run_full_cycle(self, session_id: str) -> SMESession:
        """Execute all 10 phases in order. Mandatory path for research workflows."""
        session = self._load(session_id)
        started = time.perf_counter()

        for phase in PHASE_ORDER:
            if phase not in session.phases_completed:
                session = self.execute_phase(session_id, phase)

        duration_ms = (time.perf_counter() - started) * 1000
        session.metadata["total_duration_ms"] = round(duration_ms, 3)
        session.status = SMESessionStatus.COMPLETED
        self.store.save_session(session)
        return session

    def validate_workflow_gate(
        self,
        domain: str,
        sme_session_id: str | None,
        *,
        require_completed: bool = False,
    ) -> SMESession:
        """
        Mandatory gate: research workflows must have a valid SME session.
        Raises SMEBypassError if bypass attempted.
        """
        if domain.lower() not in SME_MANDATORY_DOMAINS:
            raise SMEBypassError(
                f"Domain '{domain}' is not SME-governed. "
                f"Mandatory domains: {sorted(SME_MANDATORY_DOMAINS)}"
            )

        if not sme_session_id:
            raise SMEBypassError(
                "Research workflows must provide sme_session_id. "
                "Create a session via POST /sme/sessions before starting autonomous research."
            )

        session = self.store.get_session(sme_session_id)
        if not session:
            raise SMEBypassError(f"SME session not found: {sme_session_id}")

        if require_completed and not session.is_complete():
            raise SMEBypassError(
                f"SME session {sme_session_id} incomplete: "
                f"{len(session.phases_completed)}/{len(PHASE_ORDER)} phases done. "
                "Run POST /sme/sessions/{id}/run before starting workflow execution."
            )

        return session

    def link_workflow(self, session_id: str, workflow_id: str) -> SMESession:
        session = self._load(session_id)
        session.workflow_id = workflow_id
        session.updated_at = datetime.now(timezone.utc)
        self.store.save_session(session)
        return session

    def _load(self, session_id: str) -> SMESession:
        session = self.store.get_session(session_id)
        if not session:
            raise ValueError(f"SME session not found: {session_id}")
        return session

    def _record_provenance(self, session: SMESession) -> None:
        """Record SME completion in unified provenance store."""
        from axiom.observability.run_provenance import RunProvenance

        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        record = RunProvenance(
            run_id=session.session_id,
            run_type="sme",
            started_at=session.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            finished_at=finished,
            duration_ms=session.metadata.get("total_duration_ms", 0.0),
            config_hash=None,
            inputs={
                "engine": "scientific_method",
                "objective": session.objective,
                "domain": session.domain,
                "phases_completed": [p.value for p in session.phases_completed],
                "hypothesis_count": len(session.hypotheses),
            },
            environment=capture_environment(),
            evidence_tier={
                "aggregate": "measured",
                "phases_completed": len(session.phases_completed),
                "all_phases": session.is_complete(),
            },
            runtime={"workflow_id": session.workflow_id},
        )
        get_provenance_store(self.db_path).save(record)


def require_sme_session(
    db_path: str,
    domain: str,
    sme_session_id: str | None,
    *,
    require_completed: bool = False,
) -> SMESession:
    """Module-level gate helper for workflow and API integration."""
    return ScientificMethodEngine(db_path).validate_workflow_gate(
        domain, sme_session_id, require_completed=require_completed
    )

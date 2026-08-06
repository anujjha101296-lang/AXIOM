"""Autonomous Research Loop orchestrator — reuses WorkflowEngine for persistence."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any, Callable, Dict, Optional

from axiom.config import settings
from axiom.research.store import ResearchStore
from axiom.research_loop.benchmarks import get_benchmark, score_benchmark
from axiom.research_loop.failure_memory import FailureMemoryStore
from axiom.research_loop.schema import (
    BenchmarkScore,
    HypothesisCandidate,
    ResearchPhase,
    ResearchRunConfig,
    ResearchRunStatus,
    ResearchState,
)
from axiom.research_loop.store import ResearchLoopStore
from axiom.research_loop.workers.context import ResearchLoopContext
from axiom.research_loop.workers import (
    EvidenceVerifierWorker,
    ExperimentDesignerWorker,
    HypothesisGeneratorWorker,
    LiteratureResearcherWorker,
    ResearchPlannerWorker,
    ResearchReporterWorker,
    SkepticCriticWorker,
    SynthesisWorker,
)
from axiom.workflow import WorkflowEngine, WorkflowStatus, get_engine
from axiom.workflow.models import EventType, WorkflowEvent

logger = logging.getLogger(__name__)

_PHASE_WORKERS = [
    ("research_planner", ResearchPlannerWorker),
    ("literature_researcher", LiteratureResearcherWorker),
    ("hypothesis_generator", HypothesisGeneratorWorker),
    ("skeptic_critic", SkepticCriticWorker),
    ("experiment_designer", ExperimentDesignerWorker),
    ("evidence_verifier", EvidenceVerifierWorker),
    ("synthesis_worker", SynthesisWorker),
]


class ResearchLoopEngine:
    """
    Closed-loop autonomous research orchestrator.

    Reuses WorkflowEngine for workflow persistence, events, and artifacts.
    Maintains ResearchState with failure memory and claim verification.
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.db_path
        self.store = ResearchLoopStore(self.db_path)
        self.failure_memory = FailureMemoryStore(self.db_path)
        self.workflow_engine = get_engine(self.db_path)
        self._workers = {w().worker_type: w() for w in [
            ResearchPlannerWorker, LiteratureResearcherWorker, HypothesisGeneratorWorker,
            SkepticCriticWorker, ExperimentDesignerWorker, EvidenceVerifierWorker,
            SynthesisWorker, ResearchReporterWorker,
        ]}
        self._cancel_flags: Dict[str, asyncio.Event] = {}
        self._pause_flags: Dict[str, asyncio.Event] = {}
        self._approval_pending: Dict[str, asyncio.Event] = {}

    def create_run(
        self,
        research_question: str,
        config: ResearchRunConfig | None = None,
    ) -> ResearchState:
        config = config or ResearchRunConfig()
        run_id = str(uuid.uuid4())
        workflow = self.workflow_engine.create_workflow(
            objective=research_question,
            domain="research_loop",
            metadata={
                "run_id": run_id,
                "benchmark_id": config.benchmark_id,
                "max_iterations": config.max_iterations,
            },
        )
        state = ResearchState(
            run_id=run_id,
            workflow_id=workflow.id,
            research_question=research_question,
            max_iterations=config.max_iterations,
            benchmark_id=config.benchmark_id,
        )
        self.store.create_run(research_question, workflow.id, config, state)
        return state

    def create_benchmark_run(self, benchmark_id: str, config: ResearchRunConfig | None = None) -> ResearchState:
        bench = get_benchmark(benchmark_id)
        if not bench:
            raise ValueError(f"Unknown benchmark: {benchmark_id}")
        config = config or ResearchRunConfig()
        config.benchmark_id = benchmark_id
        return self.create_run(bench.problem_statement, config)

    async def run(self, run_id: str) -> ResearchState:
        row = self.store.get_run_row(run_id)
        if not row:
            raise ValueError(f"Run {run_id} not found")

        state = self.store.get_state(run_id)
        if not state:
            raise ValueError(f"State for run {run_id} not found")

        config = self.store.get_config(run_id)
        self.store.set_status(run_id, ResearchRunStatus.RUNNING)
        self._cancel_flags[run_id] = asyncio.Event()
        self._pause_flags[run_id] = asyncio.Event()

        research_store = None
        if config.project_id:
            research_store = ResearchStore(self.db_path, settings.research_upload_dir)

        ctx = ResearchLoopContext(
            state=state,
            failure_memory=self.failure_memory,
            research_store=research_store,
            metadata={"project_id": config.project_id},
        )

        t_start = time.monotonic()
        self._emit(state.workflow_id, EventType.WORKFLOW_STARTED, {"run_id": run_id})

        try:
            while state.current_iteration <= state.max_iterations:
                if self._cancel_flags.get(run_id, asyncio.Event()).is_set():
                    self.store.set_status(run_id, ResearchRunStatus.CANCELLED)
                    break

                if self._pause_flags.get(run_id, asyncio.Event()).is_set():
                    state.current_phase = ResearchPhase.PAUSED
                    self.store.update_state(run_id, state, ResearchRunStatus.PAUSED)
                    self._emit(state.workflow_id, EventType.WORKFLOW_PAUSED, {"iteration": state.current_iteration})
                    return state

                state.add_timeline(
                    ResearchPhase.DECOMPOSE,
                    f"Starting iteration {state.current_iteration}",
                    "research_loop_engine",
                )
                self.store.update_state(run_id, state, ResearchRunStatus.RUNNING)

                for worker_type, _ in _PHASE_WORKERS:
                    if self._cancel_flags.get(run_id, asyncio.Event()).is_set():
                        break
                    worker = self._workers[worker_type]
                    await worker.execute(ctx)
                    self.store.update_state(run_id, state)

                if config.require_approval_before_attempt:
                    approval_key = f"{run_id}:{state.current_iteration}"
                    self._approval_pending[approval_key] = asyncio.Event()
                    self.store.set_status(run_id, ResearchRunStatus.WAITING_APPROVAL)
                    await self._approval_pending[approval_key].wait()

                supported = [c for c in state.claims if c.status.value in ("SUPPORTED", "KNOWN", "FORMALLY_VERIFIED")]
                experiment_ok = any(e.success for e in state.experiments if e.iteration == state.current_iteration)

                if config.stop_on_supported_solution and supported and experiment_ok:
                    logger.info(f"Run {run_id}: stopping early — supported solution found")
                    break

                if state.current_iteration >= state.max_iterations:
                    break

                state.current_phase = ResearchPhase.REPLAN
                state.add_timeline(ResearchPhase.REPLAN, "Replanning for next iteration", "research_loop_engine")
                state.current_iteration += 1

            if not self._cancel_flags.get(run_id, asyncio.Event()).is_set():
                reporter = self._workers["research_reporter"]
                await reporter.execute(ctx)
                self.store.update_state(run_id, state, ResearchRunStatus.COMPLETED)
                self.store.set_status(run_id, ResearchRunStatus.COMPLETED)

                wf = self.workflow_engine.get_workflow(state.workflow_id)
                if wf:
                    wf.status = WorkflowStatus.COMPLETED
                    self.workflow_engine.store.save(wf)

                self._emit(state.workflow_id, EventType.WORKFLOW_COMPLETED, {
                    "run_id": run_id,
                    "iterations": state.current_iteration,
                    "confidence": state.confidence,
                })

                if state.benchmark_id:
                    self._score_benchmark_run(state, time.monotonic() - t_start, ctx.model_calls)

        except Exception as exc:
            logger.exception(f"Research loop {run_id} failed")
            self.store.set_status(run_id, ResearchRunStatus.FAILED, str(exc))
            self._emit(state.workflow_id, EventType.WORKFLOW_FAILED, {"error": str(exc)})
            raise
        finally:
            self._cancel_flags.pop(run_id, None)
            self._pause_flags.pop(run_id, None)
            if research_store:
                research_store.close()

        return state

    def _score_benchmark_run(self, state: ResearchState, duration: float, model_calls: int) -> BenchmarkScore:
        claim_texts = [c.statement for c in state.claims]
        correctness = score_benchmark(state.benchmark_id or "", state.final_report, claim_texts)
        evidence_quality = min(1.0, len(state.evidence) / max(1, len(state.subproblems)))
        recovery = len(state.failed_attempts) > 0 and any(
            c.status.value in ("SUPPORTED", "KNOWN") for c in state.claims
        )
        score = BenchmarkScore(
            benchmark_id=state.benchmark_id or "",
            run_id=state.run_id,
            solution_correctness=correctness,
            route_novelty=0.5,
            evidence_quality=evidence_quality,
            iterations_used=state.current_iteration,
            failed_approaches=len(state.failed_attempts),
            recovery_from_failure=recovery,
            human_interventions=state.human_interventions,
            model_calls=model_calls,
            duration_seconds=duration,
            hidden_solution_match=correctness,
            notes="Scored against hidden solution keywords — not a claim of discovery.",
        )
        self.store.save_benchmark_score(score)
        return score

    async def pause(self, run_id: str) -> None:
        ev = self._pause_flags.get(run_id)
        if ev:
            ev.set()

    async def resume(self, run_id: str) -> ResearchState:
        ev = self._pause_flags.get(run_id)
        if ev:
            ev.clear()
        self.store.set_status(run_id, ResearchRunStatus.RUNNING)
        return await self.run(run_id)

    async def cancel(self, run_id: str) -> None:
        ev = self._cancel_flags.get(run_id)
        if ev:
            ev.set()
        self.store.set_status(run_id, ResearchRunStatus.CANCELLED)

    def approve_iteration(self, run_id: str, iteration: int) -> None:
        key = f"{run_id}:{iteration}"
        ev = self._approval_pending.get(key)
        if ev:
            ev.set()
        state = self.store.get_state(run_id)
        if state:
            state.human_interventions += 1
            self.store.update_state(run_id, state)

    def reject_hypothesis(self, run_id: str, hypothesis_id: str, reason: str = "") -> ResearchState:
        state = self.store.get_state(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found")
        for h in state.hypotheses:
            if h.id == hypothesis_id:
                h.rejected = True
                h.rejection_reason = reason or "Rejected by researcher"
                state.human_interventions += 1
                break
        self.store.update_state(run_id, state)
        return state

    def add_evidence(self, run_id: str, source: str, content: str) -> ResearchState:
        from axiom.research_loop.schema import ClaimStatus, EvidenceItem
        state = self.store.get_state(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found")
        state.evidence.append(EvidenceItem(
            source=source,
            content=content,
            claim_status=ClaimStatus.KNOWN,
            confidence=0.9,
            iteration=state.current_iteration,
            worker_role="human",
        ))
        state.human_interventions += 1
        if source not in state.sources:
            state.sources.append(source)
        self.store.update_state(run_id, state)
        return state

    def change_objective(self, run_id: str, new_question: str) -> ResearchState:
        state = self.store.get_state(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found")
        state.research_question = new_question
        state.human_interventions += 1
        state.add_timeline(ResearchPhase.REPLAN, f"Objective changed by researcher", "human")
        self.store.update_state(run_id, state)
        return state

    def get_state(self, run_id: str) -> Optional[ResearchState]:
        return self.store.get_state(run_id)

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.store.list_runs(limit)

    def get_events(self, run_id: str) -> list:
        state = self.store.get_state(run_id)
        if not state:
            return []
        return self.workflow_engine.get_events(state.workflow_id)

    def _emit(self, workflow_id: str, event_type: EventType, payload: dict) -> None:
        self.workflow_engine.store.save_event(WorkflowEvent(
            workflow_id=workflow_id,
            event_type=event_type,
            payload=payload,
        ))


_default_engine: ResearchLoopEngine | None = None


def get_research_loop_engine(db_path: str | None = None) -> ResearchLoopEngine:
    global _default_engine
    if _default_engine is None or db_path:
        _default_engine = ResearchLoopEngine(db_path=db_path)
    return _default_engine

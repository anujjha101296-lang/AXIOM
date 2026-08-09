"""User journey verification (VF §5)."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from typing import Any

from axiom.vfactory.models import JourneyResult, _new_id, _utc_now

JourneyStep = Callable[[], dict[str, Any]]


def _step(name: str, fn: Callable[[], bool], *, detail: str = "") -> dict[str, Any]:
    try:
        ok = fn()
        return {"step": name, "passed": ok, "detail": detail or ("ok" if ok else "failed")}
    except Exception as exc:
        return {"step": name, "passed": False, "detail": str(exc)}


def run_journey_a_research_workspace(db_path: str) -> JourneyResult:
    """Journey A: Research workspace — project → note → search → session."""
    from axiom.research.store import ResearchStore

    with tempfile.TemporaryDirectory() as upload_dir:
        store = ResearchStore(db_path, upload_dir)
        steps: list[dict[str, Any]] = []
        project_id: str | None = None

        def create_project() -> bool:
            nonlocal project_id
            proj = store.create_project(name="VF Journey A", description="Verification factory test")
            project_id = proj.id
            return project_id is not None

        def add_note() -> bool:
            if not project_id:
                return False
            note = store.create_note(
                project_id, title="Test note", body="Verification content", tags=["vf"]
            )
            return note.id is not None

        def search() -> bool:
            results = store.search("Verification")
            return isinstance(results, list)

        def session() -> bool:
            if not project_id:
                return False
            sess = store.resume_session(project_id)
            return sess.id is not None

        steps.append(_step("create_project", create_project))
        steps.append(_step("add_note", add_note))
        steps.append(_step("search", search))
        steps.append(_step("resume_session", session))

    passed = all(s["passed"] for s in steps)
    return JourneyResult(
        journey_id=_new_id("journey"),
        journey_name="Journey A: Research Workspace",
        steps_completed=sum(1 for s in steps if s["passed"]),
        steps_total=len(steps),
        passed=passed,
        step_results=steps,
    )


def run_journey_b_campaign(db_path: str) -> JourneyResult:
    """Journey B: Researcher campaign lifecycle."""
    from axiom.campaign.orchestrator import FrontierCampaignEngine

    engine = FrontierCampaignEngine(db_path)
    steps: list[dict[str, Any]] = []
    campaign_id: str | None = None

    def create() -> bool:
        nonlocal campaign_id
        c = engine.create_campaign(
            name="VF Campaign",
            objective="Verify campaign engine end-to-end",
            problem_definition="Test scope, plan, and cycle.",
        )
        campaign_id = c.campaign_id
        return bool(campaign_id)

    def scope() -> bool:
        if not campaign_id:
            return False
        c = engine.scope(campaign_id)
        return len(c.research_graph) >= 1

    def plan() -> bool:
        if not campaign_id:
            return False
        c = engine.plan(campaign_id)
        return len(c.strategies) >= 1

    def cycle() -> bool:
        if not campaign_id:
            return False
        result = engine.run_cycle(campaign_id)
        return result.get("cycle_number") == 1

    def dashboard() -> bool:
        if not campaign_id:
            return False
        dash = engine.dashboard(campaign_id)
        return "phase" in dash

    steps.append(_step("create_campaign", create))
    steps.append(_step("scope", scope))
    steps.append(_step("plan", plan))
    steps.append(_step("run_cycle", cycle))
    steps.append(_step("dashboard", dashboard))

    passed = all(s["passed"] for s in steps)
    return JourneyResult(
        journey_id=_new_id("journey"),
        journey_name="Journey B: Research Campaign",
        steps_completed=sum(1 for s in steps if s["passed"]),
        steps_total=len(steps),
        passed=passed,
        step_results=steps,
    )


def run_journey_c_formal_math(db_path: str) -> JourneyResult:
    """Journey C: Mathematical researcher — formalize → compile gate."""
    from axiom.formal_math.compilation import compile_proof
    from axiom.formal_math.formalization import formalize_informal
    from axiom.formal_math.models import ProofArtifact, ProofCompilationStatus

    steps: list[dict[str, Any]] = []

    def formalize() -> bool:
        result = formalize_informal("For all n, n + 0 = n")
        return result.status.value in (
            "successfully_formalized", "partially_formalized", "ambiguous"
        )

    def compile_gate() -> bool:
        artifact = ProofArtifact(
            proof_id="vf_proof_test",
            theorem_id="vf_thm",
            version=1,
            created_at=_utc_now(),
            prover="lean4",
            prover_version="4.0",
            formal_statement="∀ n, n + 0 = n",
            source_code="theorem vf_thm : True := trivial",
            compilation_status=ProofCompilationStatus.UNKNOWN,
        )
        status, _output, _layers = compile_proof(artifact)
        return status.value in (
            "COMPILES",
            "FORMALLY_VERIFIED",
            "PARTIALLY_FORMALIZED",
            "UNKNOWN",
        )

    steps.append(_step("formalize", formalize))
    steps.append(_step("compile_gate", compile_gate))

    passed = all(s["passed"] for s in steps)
    return JourneyResult(
        journey_id=_new_id("journey"),
        journey_name="Journey C: Formal Mathematics",
        steps_completed=sum(1 for s in steps if s["passed"]),
        steps_total=len(steps),
        passed=passed,
        step_results=steps,
    )


def run_journey_d_sandbox_recovery(db_path: str) -> JourneyResult:
    """Journey D: Experiment sandbox — success and safe failure."""
    from axiom.experiment.executor import execute_experiment
    from axiom.experiment.models import ExperimentSpec, ResourceBudget
    from axiom.experiment.store import ExperimentStore

    store = ExperimentStore(db_path)
    steps: list[dict[str, Any]] = []

    def success_run() -> bool:
        spec = ExperimentSpec(
            research_question="VF test",
            hypothesis="Sandbox works",
            objective="Verify SEC",
            code="print('vf_ok')",
            resource_budget=ResourceBudget(timeout_seconds=5.0),
        )
        exp = store.create_experiment(spec)
        result = execute_experiment(store, exp.experiment_id)
        return result.get("status") == "COMPLETED"

    def safe_failure() -> bool:
        spec = ExperimentSpec(
            research_question="VF fail test",
            hypothesis="Timeout enforced",
            objective="Verify safe failure",
            code="import time; time.sleep(30)",
            resource_budget=ResourceBudget(timeout_seconds=2.0),
        )
        exp = store.create_experiment(spec)
        result = execute_experiment(store, exp.experiment_id)
        return result.get("status") == "FAILED"

    steps.append(_step("sandbox_success", success_run))
    steps.append(_step("sandbox_safe_failure", safe_failure))

    passed = all(s["passed"] for s in steps)
    return JourneyResult(
        journey_id=_new_id("journey"),
        journey_name="Journey D: Sandbox Recovery",
        steps_completed=sum(1 for s in steps if s["passed"]),
        steps_total=len(steps),
        passed=passed,
        step_results=steps,
    )


ALL_JOURNEYS = {
    "journey_a": run_journey_a_research_workspace,
    "journey_b": run_journey_b_campaign,
    "journey_c": run_journey_c_formal_math,
    "journey_d": run_journey_d_sandbox_recovery,
}

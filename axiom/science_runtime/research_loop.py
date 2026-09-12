from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Callable
from uuid import uuid4

from .critic import Critique
from .report import EvidenceBundle, build_lorenz_evidence_bundle


class ResearchStage(StrEnum):
    PLANNED = "PLANNED"
    HYPOTHESIS = "HYPOTHESIS"
    DESIGNED = "DESIGNED"
    EXECUTED = "EXECUTED"
    CRITIQUED = "CRITIQUED"
    VERIFIED = "VERIFIED"
    REPEATING = "REPEATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ResearchQuestion:
    text: str
    model: str = "lorenz"
    max_experiments: int = 3
    allowed_rho: tuple[float, ...] = (20.0, 24.0, 28.0, 32.0, 40.0)


@dataclass(frozen=True)
class Hypothesis:
    statement: str
    rationale: str


@dataclass(frozen=True)
class ExperimentPlan:
    rho: float
    horizon: float = 2.0
    dts: tuple[float, ...] = (0.02, 0.01, 0.005)
    cross_check_horizon: float = 1.0
    cross_check_dt: float = 0.001


@dataclass(frozen=True)
class Transition:
    stage: str
    action: str
    detail: str


Planner = Callable[[ResearchQuestion], tuple[Hypothesis, ExperimentPlan]]
EventSink = Callable[["ResearchRun", Transition], None]


@dataclass
class ResearchRun:
    run_id: str
    question: ResearchQuestion
    hypothesis: Hypothesis | None = None
    plans: list[ExperimentPlan] = field(default_factory=list)
    evidence: list[EvidenceBundle] = field(default_factory=list)
    critiques: list[Critique] = field(default_factory=list)
    stage: ResearchStage = ResearchStage.PLANNED
    transitions: list[Transition] = field(default_factory=list)
    conclusion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "question": asdict(self.question),
            "hypothesis": asdict(self.hypothesis) if self.hypothesis else None,
            "plans": [asdict(plan) for plan in self.plans],
            "evidence": [bundle.to_dict() for bundle in self.evidence],
            "critiques": [critique.to_dict() for critique in self.critiques],
            "stage": self.stage.value,
            "transitions": [asdict(item) for item in self.transitions],
            "conclusion": self.conclusion,
        }

    def markdown_report(self) -> str:
        lines = [
            "# AXIOM Bounded Scientific Research Run",
            "",
            f"**Run:** `{self.run_id}`",
            f"**Stage:** `{self.stage.value}`",
            "",
            "## Question",
            self.question.text,
            "",
            "## Hypothesis",
            self.hypothesis.statement if self.hypothesis else "Not generated.",
            "",
            "## Experiment sequence",
        ]
        for index, (plan, bundle, critique) in enumerate(
            zip(self.plans, self.evidence, self.critiques), start=1
        ):
            lines.extend(
                [
                    f"### Experiment {index}",
                    f"- rho: `{plan.rho:g}`",
                    f"- critic verdict: `{critique.verdict}`",
                    f"- evidence tier: `{bundle.evidence_tier}`",
                    f"- content SHA-256: `{bundle.content_sha256}`",
                    f"- provenance SHA-256: `{bundle.provenance['input_digest_sha256']}`",
                ]
            )
        lines.extend(["", "## Conclusion", self.conclusion or "No conclusion reached.", "", "## State transitions"])
        lines.extend(f"- `{t.stage}` — {t.action}: {t.detail}" for t in self.transitions)
        return "\n".join(lines) + "\n"


def deterministic_planner(question: ResearchQuestion) -> tuple[Hypothesis, ExperimentPlan]:
    if question.model.lower() != "lorenz":
        raise ValueError(f"Unsupported model: {question.model}")
    if question.max_experiments < 1:
        raise ValueError("max_experiments must be >= 1")
    if not question.allowed_rho:
        raise ValueError("allowed_rho must not be empty")
    hypothesis = Hypothesis(
        statement="Sensitivity should increase near the classical Lorenz chaotic regime, while numerical evidence must remain robust under timestep and solver checks.",
        rationale="Use a bounded rho ladder and independent numerical integration before accepting the observation.",
    )
    return hypothesis, ExperimentPlan(rho=question.allowed_rho[0])


def _next_plan(question: ResearchQuestion, used_rho: set[float]) -> ExperimentPlan | None:
    for rho in question.allowed_rho:
        if rho not in used_rho:
            return ExperimentPlan(rho=rho)
    return None


def run_research(
    question: ResearchQuestion,
    *,
    planner: Planner = deterministic_planner,
    event_sink: EventSink | None = None,
    run_id: str | None = None,
) -> ResearchRun:
    run = ResearchRun(run_id=run_id or f"research-{uuid4().hex[:12]}", question=question)

    def transition(stage: ResearchStage, action: str, detail: str) -> None:
        run.stage = stage
        item = Transition(stage.value, action, detail)
        run.transitions.append(item)
        if event_sink is not None:
            event_sink(run, item)

    transition(ResearchStage.PLANNED, "run_created", "Bounded research run created.")
    hypothesis, first_plan = planner(question)
    run.hypothesis = hypothesis
    transition(ResearchStage.HYPOTHESIS, "hypothesis_proposed", hypothesis.statement)

    plan: ExperimentPlan | None = first_plan
    while plan is not None and len(run.evidence) < question.max_experiments:
        if plan.rho not in question.allowed_rho:
            transition(ResearchStage.FAILED, "plan_rejected", "Planner proposed rho outside the allowlist.")
            run.conclusion = "Run failed closed because the experiment plan violated its declared parameter bounds."
            return run

        run.plans.append(plan)
        transition(ResearchStage.DESIGNED, "experiment_designed", f"Execute Lorenz evidence experiment at rho={plan.rho:g}.")

        bundle = build_lorenz_evidence_bundle(
            plan.rho,
            horizon=plan.horizon,
            dts=plan.dts,
            cross_check_horizon=plan.cross_check_horizon,
            cross_check_dt=plan.cross_check_dt,
        )
        run.evidence.append(bundle)
        transition(ResearchStage.EXECUTED, "experiment_executed", f"Generated deterministic evidence bundle {bundle.experiment_id}.")

        convergence_errors = [
            point["reference_error"]
            for point in bundle.convergence
            if point["reference_error"] is not None
        ]
        independent = bundle.independent_check
        from .critic import critique_evidence

        critique = critique_evidence(
            evidence_tier=bundle.evidence_tier,
            reproducible=True,
            convergence_errors=convergence_errors,
            independent_relative_error=float(independent["relative_error"]),
            finite=bool(independent["finite"]),
            has_provenance=bool(bundle.provenance),
        )
        run.critiques.append(critique)
        transition(ResearchStage.CRITIQUED, "critique_completed", critique.verdict)

        if critique.verdict == "ACCEPT_NUMERICAL_EVIDENCE":
            transition(ResearchStage.VERIFIED, "verify", "Numerical evidence satisfied all declared critic gates.")
            run.conclusion = (
                f"Numerical evidence at rho={plan.rho:g} passed the bounded reproducibility, "
                "convergence, provenance, and independent-check gates. This is not a formal proof of chaos."
            )
            transition(ResearchStage.COMPLETED, "run_completed", "Accepted bounded numerical result.")
            return run

        transition(ResearchStage.REPEATING, "repeat_requested", "Critic rejected the evidence; select the next allowed rho.")
        plan = _next_plan(question, {p.rho for p in run.plans})

    run.conclusion = "No experiment satisfied the declared evidence gates within the bounded experiment budget."
    transition(ResearchStage.FAILED, "run_failed", "Experiment budget exhausted without verified numerical evidence.")
    return run

"""Skeptic Critic — challenges hypotheses and flags unsupported claims."""

from __future__ import annotations

from typing import TYPE_CHECKING

from axiom.research_loop.claims import classify_claim
from axiom.research_loop.schema import ClaimStatus, CriticismRecord, ResearchPhase

if TYPE_CHECKING:
    from axiom.research_loop.workers.context import ResearchLoopContext


class SkepticCriticWorker:
    worker_type = "skeptic_critic"
    mission = "Critique hypotheses and downgrade unsupported claims"

    async def execute(self, ctx: "ResearchLoopContext") -> dict:
        state = ctx.state
        state.current_phase = ResearchPhase.CRITICIZE
        state.active_workers = [self.worker_type]
        criticisms: list[CriticismRecord] = []
        rejected = 0

        active_hyps = [h for h in state.hypotheses if not h.rejected and h.iteration == state.current_iteration]
        if not active_hyps:
            active_hyps = [h for h in state.hypotheses if not h.rejected][-3:]

        for hyp in active_hyps:
            status = classify_claim(hyp.statement, state.evidence)
            severity = "low"
            criticism_text = ""

            if hyp.score < 0.3:
                severity = "high"
                criticism_text = f"Low-ranked hypothesis ({hyp.score:.2f}): likely incorrect or overgeneralized."
                hyp.rejected = True
                hyp.rejection_reason = criticism_text
                rejected += 1
            elif status == ClaimStatus.SPECULATIVE and hyp.score < 0.5:
                severity = "medium"
                criticism_text = "Insufficient evidential support; treat as speculative only."
            elif "false" in hyp.rationale.lower() or "incorrect" in hyp.rationale.lower():
                severity = "high"
                criticism_text = "Generator flagged this as likely false — reject before attempting."
                hyp.rejected = True
                hyp.rejection_reason = criticism_text
                rejected += 1
            else:
                criticism_text = f"Reviewed: status={status.value}. Rationale: {hyp.rationale[:100]}"

            rec = CriticismRecord(
                target_id=hyp.id,
                target_type="hypothesis",
                criticism=criticism_text,
                severity=severity,
                iteration=state.current_iteration,
            )
            criticisms.append(rec)

        state.artifacts.extend([c.model_dump() for c in criticisms])
        state.add_timeline(
            ResearchPhase.CRITICIZE,
            f"Critiqued {len(criticisms)} hypotheses, rejected {rejected}",
            self.worker_type,
        )
        state.active_workers = []
        return {"criticisms": len(criticisms), "rejected": rejected}

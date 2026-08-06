"""Synthesis Worker — integrates findings and identifies gaps."""

from __future__ import annotations

from typing import TYPE_CHECKING

from axiom.research_loop.schema import ClaimStatus, ResearchPhase

if TYPE_CHECKING:
    from axiom.research_loop.workers.context import ResearchLoopContext


class SynthesisWorker:
    worker_type = "synthesis_worker"
    mission = "Synthesize evidence, identify gaps, update confidence"

    async def execute(self, ctx: "ResearchLoopContext") -> dict:
        state = ctx.state
        state.current_phase = ResearchPhase.SYNTHESIZE
        state.active_workers = [self.worker_type]

        supported = [c for c in state.claims if c.status in (ClaimStatus.SUPPORTED, ClaimStatus.KNOWN, ClaimStatus.FORMALLY_VERIFIED)]
        speculative = [c for c in state.claims if c.status == ClaimStatus.SPECULATIVE]
        disproved = [c for c in state.claims if c.status == ClaimStatus.DISPROVED]

        if supported:
            state.confidence = min(0.95, 0.4 + 0.15 * len(supported))
        elif state.experiments and any(e.success for e in state.experiments):
            state.confidence = 0.65
        else:
            state.confidence = max(0.1, 0.3 - 0.05 * len(disproved))

        gaps = []
        for sub in state.subproblems:
            covered = any(sub.lower()[:20] in c.statement.lower() for c in state.claims)
            if not covered:
                gaps.append(f"Subproblem not yet addressed by verified claims: {sub[:60]}")

        state.uncertainties.extend(gaps)
        state.current_phase = ResearchPhase.IDENTIFY_GAPS
        state.add_timeline(
            ResearchPhase.IDENTIFY_GAPS,
            f"Synthesis: {len(supported)} supported, {len(speculative)} speculative, confidence={state.confidence:.2f}",
            self.worker_type,
        )
        state.active_workers = []
        return {"confidence": state.confidence, "gaps": len(gaps)}

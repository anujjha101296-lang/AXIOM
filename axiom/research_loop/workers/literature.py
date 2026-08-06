"""Literature Researcher — retrieves evidence from ResearchStore."""

from __future__ import annotations

from typing import TYPE_CHECKING

from axiom.research_loop.schema import ClaimStatus, EvidenceItem, ResearchPhase

if TYPE_CHECKING:
    from axiom.research_loop.workers.context import ResearchLoopContext


class LiteratureResearcherWorker:
    worker_type = "literature_researcher"
    mission = "Retrieve and attribute evidence from project documents and notes"

    async def execute(self, ctx: "ResearchLoopContext") -> dict:
        state = ctx.state
        state.current_phase = ResearchPhase.RETRIEVE
        state.active_workers = [self.worker_type]
        evidence_items: list[EvidenceItem] = []

        if ctx.research_store and state.benchmark_id is None:
            project_id = ctx.metadata.get("project_id")
            if project_id:
                try:
                    for sub in state.subproblems[:3]:
                        results = ctx.research_store.search(sub, project_id=project_id, limit=3)
                        for r in results:
                            item = EvidenceItem(
                                source=r.title,
                                content=r.snippet,
                                claim_status=ClaimStatus.SUPPORTED,
                                confidence=0.75,
                                iteration=state.current_iteration,
                                worker_role=self.worker_type,
                            )
                            evidence_items.append(item)
                            if r.title not in state.sources:
                                state.sources.append(r.title)
                except Exception:
                    pass

        if not evidence_items:
            for i, sub in enumerate(state.subproblems):
                item = EvidenceItem(
                    source=f"problem_structure:{i+1}",
                    content=f"Subproblem context: {sub}. Derived from problem decomposition, not external citation.",
                    claim_status=ClaimStatus.KNOWN,
                    confidence=0.5,
                    iteration=state.current_iteration,
                    worker_role=self.worker_type,
                )
                evidence_items.append(item)

        state.evidence.extend(evidence_items)
        state.add_timeline(
            ResearchPhase.RETRIEVE,
            f"Retrieved {len(evidence_items)} evidence items",
            self.worker_type,
        )
        state.active_workers = []
        return {"evidence_count": len(evidence_items)}

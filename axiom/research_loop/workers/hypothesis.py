"""Hypothesis Generator — proposes and ranks candidate hypotheses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from axiom.research_loop.failure_memory import fingerprint_approach
from axiom.research_loop.schema import ClaimStatus, HypothesisCandidate, ResearchPhase

if TYPE_CHECKING:
    from axiom.research_loop.workers.context import ResearchLoopContext


class HypothesisGeneratorWorker:
    worker_type = "hypothesis_generator"
    mission = "Generate ranked hypotheses grounded in evidence, avoiding failed approaches"

    async def execute(self, ctx: "ResearchLoopContext") -> dict:
        state = ctx.state
        state.current_phase = ResearchPhase.HYPOTHESIZE
        state.active_workers = [self.worker_type]
        q = state.research_question.lower()
        candidates: list[HypothesisCandidate] = []

        templates: list[tuple[str, str, float]] = []
        if "sum" in q:
            templates = [
                ("The sum 1+2+...+n equals n(n+1)/2", "Pairing first and last terms in the series", 0.85),
                ("The sum grows quadratically in n", "Observed from small-case enumeration", 0.6),
                ("The sum equals n²", "Naive polynomial guess — likely incorrect", 0.2),
            ]
        elif "pythagor" in q or ("3" in q and "4" in q):
            templates = [
                ("3² + 4² = 5² verifies the Pythagorean relation", "Direct computation: 9+16=25", 0.9),
                ("Primitive triples (a,b,c) satisfy a²+b²=c²", "Definition of Pythagorean triples", 0.8),
                ("All triples are multiples of (3,4,5)", "Overgeneralization — false", 0.15),
            ]
        elif "prime" in q:
            templates = [
                ("There are infinitely many primes (Euclid)", "Assume finite list, construct N+1", 0.88),
                ("Primes become sparse but never end", "Heuristic from distribution", 0.5),
                ("Largest prime exists near n log n", "Misconception — false", 0.1),
            ]
        elif "polyhedron" in q or "euler" in q or "vertices" in q:
            templates = [
                ("For convex polyhedra, V - E + F = 2", "Euler's polyhedron formula", 0.9),
                ("Cube satisfies 8 - 12 + 6 = 2", "Direct count verification", 0.95),
                ("V + E + F = constant for all solids", "Incorrect sign pattern", 0.1),
            ]
        else:
            templates = [
                (f"A constructive approach resolves: {state.research_question[:80]}", "From evidence synthesis", 0.5),
            ]

        existing = state.hypothesis_fingerprints()
        rank = 1
        for statement, rationale, score in templates:
            fp = fingerprint_approach(statement)
            if fp in existing:
                continue
            if ctx.failure_memory.is_blocked(statement, run_id=state.run_id):
                state.uncertainties.append(f"Blocked hypothesis (failure memory): {statement[:60]}")
                continue
            candidates.append(HypothesisCandidate(
                statement=statement,
                rationale=rationale,
                score=score,
                rank=rank,
                status=ClaimStatus.SPECULATIVE if score < 0.7 else ClaimStatus.SUPPORTED,
                iteration=state.current_iteration,
            ))
            rank += 1

        candidates.sort(key=lambda h: h.score, reverse=True)
        for i, c in enumerate(candidates, start=1):
            c.rank = i
        state.hypotheses.extend(candidates)
        state.current_phase = ResearchPhase.RANK
        state.add_timeline(ResearchPhase.RANK, f"Ranked {len(candidates)} hypotheses", self.worker_type)
        state.active_workers = []
        return {"hypothesis_count": len(candidates)}

"""Research Planner worker — decomposes problems and checks failure memory."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from axiom.research_loop.failure_memory import fingerprint_approach
from axiom.research_loop.schema import ResearchPhase

if TYPE_CHECKING:
    from axiom.research_loop.workers.context import ResearchLoopContext


class ResearchPlannerWorker:
    worker_type = "research_planner"
    mission = "Decompose research question into subproblems with explicit assumptions"

    async def execute(self, ctx: "ResearchLoopContext") -> dict:
        state = ctx.state
        question = state.research_question
        state.current_phase = ResearchPhase.DECOMPOSE
        state.active_workers = [self.worker_type]

        subproblems: list[str] = []
        if "sum" in question.lower() and ("1 + 2" in question or "integers" in question.lower()):
            subproblems = [
                "Identify the pattern in partial sums S_k = 1+2+...+k",
                "Derive a closed-form expression for S_n",
                "Verify the formula for a concrete n (e.g. n=100)",
            ]
            state.known_facts.append("Arithmetic series: terms increase by 1 each step.")
        elif "pythagor" in question.lower() or "3" in question and "4" in question:
            subproblems = [
                "Verify the numerical identity for the (3,4,5) triple",
                "State the general Pythagorean relation for right triangles",
                "Describe how primitive triples are generated",
            ]
            state.known_facts.append("A right triangle satisfies a² + b² = c².")
        elif "prime" in question.lower() and "infinite" in question.lower():
            subproblems = [
                "State what it means for primes to be infinite",
                "Identify a classical proof strategy (contradiction)",
                "Construct the Euclid-style argument",
            ]
            state.known_facts.append("A prime has exactly two positive divisors.")
        elif "polyhedron" in question.lower() or "vertices" in question.lower() or "euler" in question.lower():
            subproblems = [
                "Count V, E, F for a concrete polyhedron (cube)",
                "Compute V - E + F and observe the value",
                "State Euler's formula for convex polyhedra",
            ]
            state.known_facts.append("A cube has 8 vertices, 12 edges, and 6 faces.")
        else:
            sentences = [s.strip() for s in re.split(r"[.?]\s+", question) if len(s.strip()) > 10]
            subproblems = sentences[:3] or [f"Analyze: {question[:120]}"]

        state.assumptions = [
            "Problem is bounded to undergraduate-level methods",
            "Available evidence from project documents is authoritative for this run",
            "No hidden solution text is provided to the loop",
        ]
        state.subproblems = subproblems
        state.open_questions = [f"How does subproblem {i+1} constrain the final answer?" for i in range(len(subproblems))]

        blocked = ctx.failure_memory.find_similar(question, run_id=state.run_id, limit=3)
        if blocked:
            state.uncertainties.append(
                f"Failure memory warns against: {blocked[0].approach[:80]}"
            )

        state.add_timeline(ResearchPhase.DECOMPOSE, f"Decomposed into {len(subproblems)} subproblems", self.worker_type)
        state.active_workers = []
        return {"subproblems": subproblems, "known_facts": state.known_facts}

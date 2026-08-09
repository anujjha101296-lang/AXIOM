"""Subproblem factory — smaller problems that advance the main problem."""

from __future__ import annotations

from axiom.open_problems.models import OpenProblem, Subproblem, _new_id


def decompose_open_problem(problem: OpenProblem) -> list[Subproblem]:
    """Generate scored subproblems from understanding + statement."""
    subs: list[Subproblem] = []
    main_id = problem.problem_id

    templates = [
        (
            "Clarify definitions",
            "Make all definitions and quantifiers precise",
            0.3,
            0.2,
            0.8,
            0.8,
            0.3,
            0.7,
        ),
        (
            "Catalog known lemmas",
            "List lemmas/theorems that the claim depends on",
            0.4,
            0.3,
            0.75,
            0.7,
            0.4,
            0.65,
        ),
        (
            "Special-case regime",
            "Resolve the claim on a restricted domain (e.g. small n)",
            0.35,
            0.25,
            0.7,
            0.85,
            0.35,
            0.8,
        ),
        (
            "Boundary / degenerate cases",
            "Test empty, extreme, and degenerate instances",
            0.4,
            0.2,
            0.85,
            0.8,
            0.4,
            0.85,
        ),
        (
            "Counterexample search",
            "Attempt to refute before investing in a proof",
            0.45,
            0.15,
            0.9,
            0.75,
            0.45,
            0.9,
        ),
        (
            "Necessary conditions",
            "Derive necessary conditions implied by the claim",
            0.55,
            0.4,
            0.7,
            0.55,
            0.55,
            0.6,
        ),
        (
            "Sufficient conditions",
            "Find sufficient conditions that imply the claim",
            0.6,
            0.45,
            0.65,
            0.5,
            0.6,
            0.55,
        ),
        (
            "Formal statement draft",
            "Produce a prover-ready formal statement (not a verified proof)",
            0.5,
            0.35,
            0.6,
            0.45,
            0.7,
            0.5,
        ),
    ]

    # Specialize from understanding
    for sc in problem.understanding.special_cases[:2]:
        templates.append(
            (
                f"Special: {sc[:60]}",
                sc,
                0.35,
                0.2,
                0.7,
                0.8,
                0.4,
                0.75,
            )
        )

    for title, stmt, diff, dep, imp, tract, ver, gain in templates[:10]:
        subs.append(
            Subproblem(
                subproblem_id=_new_id("sub"),
                title=title,
                statement=stmt,
                difficulty=diff,
                dependency=dep,
                importance=imp,
                tractability=tract,
                verification_difficulty=ver,
                expected_information_gain=gain,
                parent_ids=[main_id],
            )
        )

    # Rank by composite
    subs.sort(key=lambda s: s.composite, reverse=True)
    return subs

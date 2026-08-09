"""Research question expansion (SKAI §11)."""

from __future__ import annotations


def expand_research_question(main_question: str) -> list[str]:
    """Expand a research question into sub-questions for planning."""
    base = main_question.strip().rstrip("?")
    return [
        f"What is already known about: {base}?",
        f"What assumptions does the approach require for: {base}?",
        f"Has a similar approach been tried before for: {base}?",
        f"What failed in prior attempts related to: {base}?",
        f"What variants of the method exist for: {base}?",
        f"What related problems have been solved near: {base}?",
        f"Can the method transfer to adjacent problems of: {base}?",
        f"What counterexamples exist related to: {base}?",
        f"What remains unresolved about: {base}?",
    ]

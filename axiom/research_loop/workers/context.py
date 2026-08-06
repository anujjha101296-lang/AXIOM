"""Shared context for research loop workers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from axiom.research_loop.failure_memory import FailureMemoryStore
    from axiom.research_loop.schema import ResearchState
    from axiom.research.store import ResearchStore


@dataclass
class ResearchLoopContext:
    state: "ResearchState"
    failure_memory: "FailureMemoryStore"
    research_store: Optional["ResearchStore"] = None
    model_calls: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def bump_model_calls(self, n: int = 1) -> None:
        self.model_calls += n

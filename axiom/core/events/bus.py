"""
In-Process Event Bus — AXIOM Event-Driven Architecture
=======================================================
A lightweight publish/subscribe bus for internal AXIOM events.
Supports synchronous and async handlers.

Usage:
    from axiom.core.events.bus import event_bus, AxiomEvent

    # Subscribe
    @event_bus.subscribe("hypothesis.generated")
    def on_hypothesis(event: AxiomEvent) -> None:
        print(f"New hypothesis: {event.payload}")

    # Publish
    await event_bus.publish(AxiomEvent(
        topic="hypothesis.generated",
        payload={"node_id": "abc", "statement": "..."},
    ))
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Union
from uuid import uuid4

from axiom.observability.logger import get_logger

logger = get_logger(__name__)

Handler = Union[
    Callable[["AxiomEvent"], None],
    Callable[["AxiomEvent"], Awaitable[None]],
]


@dataclass
class AxiomEvent:
    """A typed event envelope published on the AXIOM event bus."""
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = ""


# ── Well-known topic constants ────────────────────────────────────────────────
class Topics:
    PAPER_INGESTED          = "paper.ingested"
    CLAIM_EXTRACTED         = "claim.extracted"
    HYPOTHESIS_GENERATED    = "hypothesis.generated"
    SMT_CHECK_COMPLETED     = "smt.check.completed"
    MCTS_PROOF_FOUND        = "mcts.proof.found"
    MCTS_PROOF_FAILED       = "mcts.proof.failed"
    SELF_IMPROVE_COMPLETED  = "self_improve.completed"
    GRAPH_UPDATED           = "graph.updated"
    MEMORY_UPDATED          = "memory.updated"


class EventBus:
    """
    Singleton in-process event bus.

    Handlers are called in subscription order.
    Async handlers are awaited; sync handlers are called directly.
    Errors in one handler do NOT prevent other handlers from running.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Handler]] = {}
        self._wildcard_handlers: List[Handler] = []
        self._event_history: List[AxiomEvent] = []
        self._max_history = 500

    def subscribe(self, topic: str) -> Callable[[Handler], Handler]:
        """Decorator: subscribe a function to a topic."""
        def decorator(fn: Handler) -> Handler:
            self._handlers.setdefault(topic, []).append(fn)
            logger.debug(f"Subscribed {fn.__name__} to topic '{topic}'")
            return fn
        return decorator

    def subscribe_all(self, fn: Handler) -> None:
        """Subscribe to every topic (wildcard)."""
        self._wildcard_handlers.append(fn)

    async def publish(self, event: AxiomEvent) -> None:
        """Publish an event and call all matching subscribers."""
        logger.debug(
            f"Event published",
            extra={"topic": event.topic, "event_id": event.event_id, "source": event.source}
        )
        # Store in history (capped)
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        handlers = self._handlers.get(event.topic, []) + self._wildcard_handlers
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                logger.error(
                    f"Handler error for topic '{event.topic}'",
                    extra={"handler": getattr(handler, "__name__", str(handler)), "error": str(exc)}
                )

    def publish_sync(self, event: AxiomEvent) -> None:
        """
        Synchronous publish — runs the event loop if needed.
        Prefer `await publish(event)` inside async contexts.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.publish(event))
            else:
                loop.run_until_complete(self.publish(event))
        except RuntimeError:
            asyncio.run(self.publish(event))

    def recent_events(self, topic: str | None = None, limit: int = 50) -> List[AxiomEvent]:
        """Return recent events, optionally filtered by topic."""
        events = self._event_history
        if topic:
            events = [e for e in events if e.topic == topic]
        return events[-limit:]

    def clear_history(self) -> None:
        self._event_history.clear()


# Global singleton
event_bus = EventBus()

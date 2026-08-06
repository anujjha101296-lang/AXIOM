"""
AXIOM Workflow Engine — Event Bus
==================================
In-process async event bus using asyncio queues.
Supports pub/sub for workflow lifecycle events.
"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Callable, Awaitable

from .models import WorkflowEvent, EventType

logger = logging.getLogger(__name__)

# Handler type: async function that receives an event
EventHandler = Callable[[WorkflowEvent], Awaitable[None]]


class EventBus:
    """
    Lightweight async event bus.

    Usage:
        bus = EventBus()
        bus.subscribe(EventType.TASK_COMPLETED, my_handler)
        await bus.publish(WorkflowEvent(...))
    """

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        self._wildcard_handlers: list[EventHandler] = []
        self._queue: asyncio.Queue[WorkflowEvent] = asyncio.Queue()
        self._running = False
        self._task: asyncio.Task | None = None

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type."""
        self._handlers[event_type].append(handler)
        logger.debug(f"EventBus: subscribed handler to {event_type}")

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler to ALL event types (wildcard)."""
        self._wildcard_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def publish(self, event: WorkflowEvent) -> None:
        """Publish an event. All subscribed handlers are called asynchronously."""
        await self._queue.put(event)

    async def publish_sync(self, event: WorkflowEvent) -> None:
        """Publish and immediately dispatch (await all handlers before returning)."""
        await self._dispatch(event)

    async def _dispatch(self, event: WorkflowEvent) -> None:
        handlers = self._handlers.get(event.event_type, []) + self._wildcard_handlers
        if not handlers:
            return
        results = await asyncio.gather(
            *[h(event) for h in handlers],
            return_exceptions=True,
        )
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"EventBus: handler error for {event.event_type}: {result}")

    async def start(self) -> None:
        """Start background event processing loop."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("EventBus: started")

    async def stop(self) -> None:
        """Stop the event processing loop gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus: stopped")

    async def _loop(self) -> None:
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                await self._dispatch(event)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"EventBus loop error: {e}")

    async def drain(self) -> None:
        """Process all queued events before returning."""
        while not self._queue.empty():
            event = self._queue.get_nowait()
            await self._dispatch(event)
            self._queue.task_done()


# Global singleton bus — can be overridden in tests
_global_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus


def reset_event_bus() -> None:
    """Reset the global bus — useful in tests."""
    global _global_bus
    _global_bus = None

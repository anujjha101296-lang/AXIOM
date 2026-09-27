"""OpenTelemetry instrumentation for AXIOM scientific execution.

This module intentionally depends on the OpenTelemetry API only. The running
application may install/configure an OpenTelemetry SDK and exporter; without
one, the API remains a no-op and scientific execution is unaffected.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from opentelemetry import metrics, trace
from opentelemetry.trace import Span, Status, StatusCode

TRACER_NAME = "axiom.science_runtime"
TRACER_VERSION = "0.1"
tracer = trace.get_tracer(TRACER_NAME, TRACER_VERSION)
meter = metrics.get_meter(TRACER_NAME, TRACER_VERSION)

research_transitions = meter.create_counter(
    "axiom.research.transitions",
    unit="1",
    description="Scientific research lifecycle transitions.",
)
research_experiments = meter.create_counter(
    "axiom.research.experiments",
    unit="1",
    description="Deterministic scientific experiments started.",
)
research_failures = meter.create_counter(
    "axiom.research.failures",
    unit="1",
    description="Scientific research failures by stable failure class.",
)
experiment_duration = meter.create_histogram(
    "axiom.research.experiment.duration",
    unit="s",
    description="Duration of deterministic scientific experiment execution.",
)


def record_transition(
    *,
    run_id: str,
    sequence: int,
    stage: str,
    action: str,
) -> None:
    """Emit a low-cardinality transition metric and span."""
    attributes = {
        "axiom.run_id": run_id,
        "axiom.event.sequence": sequence,
        "axiom.research.stage": stage,
        "axiom.research.action": action,
    }
    research_transitions.add(
        1,
        {
            "axiom.research.stage": stage,
            "axiom.research.action": action,
        },
    )
    with tracer.start_as_current_span("axiom.research.transition") as span:
        span.set_attributes(attributes)


def record_failure(*, failure_class: str) -> None:
    """Record a stable failure class; never attach exception text to metrics."""
    research_failures.add(1, {"axiom.failure.class": failure_class})


@contextmanager
def experiment_span(
    *,
    run_id: str,
    rho: float,
) -> Iterator[Span]:
    """Trace one deterministic experiment without exposing scientific payloads."""
    research_experiments.add(1)
    with tracer.start_as_current_span("axiom.science.experiment") as span:
        span.set_attributes(
            {
                "axiom.run_id": run_id,
                "axiom.experiment.model": "lorenz",
                "axiom.experiment.rho": rho,
            }
        )
        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))
            record_failure(failure_class="experiment_exception")
            raise

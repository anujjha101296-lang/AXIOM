from __future__ import annotations

from contextlib import contextmanager

from axiom.observability import science


class _FakeSpan:
    def __init__(self) -> None:
        self.attributes: dict[str, object] = {}
        self.status = None
        self.exceptions: list[Exception] = []

    def set_attribute(self, key: str, value: object) -> None:
        self.attributes[key] = value

    def set_attributes(self, values: dict[str, object]) -> None:
        self.attributes.update(values)

    def set_status(self, status: object) -> None:
        self.status = status

    def record_exception(self, exc: Exception) -> None:
        self.exceptions.append(exc)


class _FakeTracer:
    def __init__(self) -> None:
        self.spans: list[tuple[str, _FakeSpan]] = []

    @contextmanager
    def start_as_current_span(self, name: str):
        span = _FakeSpan()
        self.spans.append((name, span))
        yield span


class _FakeCounter:
    def __init__(self) -> None:
        self.calls: list[tuple[float, dict[str, str]]] = []

    def add(self, amount: float, attributes: dict[str, str] | None = None) -> None:
        self.calls.append((amount, attributes or {}))


def test_transition_telemetry_contains_correlation_without_payload(monkeypatch) -> None:
    tracer = _FakeTracer()
    counter = _FakeCounter()
    monkeypatch.setattr(science, "tracer", tracer)
    monkeypatch.setattr(science, "research_transitions", counter)

    science.record_transition(
        run_id="research-123",
        sequence=7,
        stage="EXECUTED",
        action="experiment_executed",
    )

    assert counter.calls == [
        (
            1,
            {
                "axiom.research.stage": "EXECUTED",
                "axiom.research.action": "experiment_executed",
            },
        )
    ]
    name, span = tracer.spans[0]
    assert name == "axiom.research.transition"
    assert span.attributes == {
        "axiom.run_id": "research-123",
        "axiom.event.sequence": 7,
        "axiom.research.stage": "EXECUTED",
        "axiom.research.action": "experiment_executed",
    }


def test_experiment_span_records_failure_without_payload(monkeypatch) -> None:
    tracer = _FakeTracer()
    failures = _FakeCounter()
    monkeypatch.setattr(science, "tracer", tracer)
    monkeypatch.setattr(science, "research_failures", failures)

    try:
        with science.experiment_span(run_id="research-123", rho=28.0):
            raise RuntimeError("scientific details must not become metric labels")
    except RuntimeError:
        pass

    name, span = tracer.spans[0]
    assert name == "axiom.science.experiment"
    assert span.attributes["axiom.run_id"] == "research-123"
    assert span.attributes["axiom.experiment.model"] == "lorenz"
    assert span.attributes["axiom.experiment.rho"] == 28.0
    assert "scientific details" not in str(span.attributes)
    assert failures.calls == [(1, {"axiom.failure.class": "experiment_exception"})]


def test_persistence_span_excludes_event_payload(monkeypatch) -> None:
    tracer = _FakeTracer()
    monkeypatch.setattr(science, "tracer", tracer)

    with science.persistence_span(
        operation="append_event",
        run_id="research-123",
        event_type="EXECUTE",
    ):
        pass

    name, span = tracer.spans[0]
    assert name == "axiom.persistence.operation"
    assert span.attributes == {
        "axiom.run_id": "research-123",
        "axiom.persistence.operation": "append_event",
        "axiom.persistence.event_type": "EXECUTE",
    }

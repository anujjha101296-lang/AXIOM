"""AXIOM Cognitive Architecture — permanent orchestration engine."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from axiom.cognitive.adapters import LayerAdapter
from axiom.cognitive.model_provider import get_model_provider
from axiom.cognitive.models import (
    LAYER_ORDER,
    CognitiveCycle,
    CognitiveCycleStatus,
    CognitiveLayer,
)
from axiom.cognitive.store import CognitiveStore
from axiom.observability.run_provenance import RunProvenance, capture_environment, get_provenance_store


class CognitiveArchitecture:
    """
    Permanent cognitive operating model for all AXIOM reasoning.
    Models are interchangeable; layers delegate to existing subsystems.
    """

    def __init__(self, db_path: str, model_provider_id: str = "default") -> None:
        self.db_path = db_path
        self.model_provider_id = model_provider_id
        self.store = CognitiveStore(db_path)
        self._provider = get_model_provider(model_provider_id)
        self._adapter = LayerAdapter(db_path, self._provider)

    def create_cycle(
        self,
        objective: str,
        domain: str = "research",
        context: dict | None = None,
        model_provider: str | None = None,
    ) -> CognitiveCycle:
        provider_id = model_provider or self.model_provider_id
        if provider_id != self.model_provider_id:
            self._provider = get_model_provider(provider_id)
            self._adapter = LayerAdapter(self.db_path, self._provider)

        cycle = CognitiveCycle(
            objective=objective,
            domain=domain,
            model_provider=provider_id,
            status=CognitiveCycleStatus.IN_PROGRESS,
            context=context or {},
        )
        self.store.save(cycle)
        return cycle

    def execute_layer(self, cycle_id: str, layer: CognitiveLayer | None = None) -> CognitiveCycle:
        cycle = self._load(cycle_id)
        target = layer or cycle.current_layer

        if target in cycle.layers_completed:
            raise ValueError(f"Layer {target.value} already completed.")

        idx = LAYER_ORDER.index(target)
        if idx > 0 and LAYER_ORDER[idx - 1] not in cycle.layers_completed:
            raise ValueError(f"Prior layer {LAYER_ORDER[idx - 1].value} not completed.")

        output = self._adapter.execute(cycle, target)
        cycle.layer_outputs.append(output)

        if not output.completed:
            cycle.status = CognitiveCycleStatus.FAILED
            self.store.save(cycle)
            raise RuntimeError(f"Layer {target.value} failed: {output.errors}")

        cycle.layers_completed.append(target)
        next_idx = idx + 1
        if next_idx < len(LAYER_ORDER):
            cycle.current_layer = LAYER_ORDER[next_idx]
        else:
            cycle.status = CognitiveCycleStatus.COMPLETED
            self._record_provenance(cycle)

        cycle.updated_at = datetime.now(timezone.utc)
        self.store.save(cycle)
        return cycle

    def run_full_cycle(self, cycle_id: str) -> CognitiveCycle:
        cycle = self._load(cycle_id)
        started = time.perf_counter()

        for layer in LAYER_ORDER:
            if layer not in cycle.layers_completed:
                cycle = self.execute_layer(cycle_id, layer)

        cycle.context["total_duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
        cycle.status = CognitiveCycleStatus.COMPLETED
        self.store.save(cycle)
        return cycle

    def link_sme(self, cycle_id: str, sme_session_id: str) -> CognitiveCycle:
        cycle = self._load(cycle_id)
        cycle.sme_session_id = sme_session_id
        cycle.updated_at = datetime.now(timezone.utc)
        self.store.save(cycle)
        return cycle

    def _load(self, cycle_id: str) -> CognitiveCycle:
        cycle = self.store.get(cycle_id)
        if not cycle:
            raise ValueError(f"Cognitive cycle not found: {cycle_id}")
        return cycle

    def _record_provenance(self, cycle: CognitiveCycle) -> None:
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        record = RunProvenance(
            run_id=cycle.cycle_id,
            run_type="aca",
            started_at=cycle.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            finished_at=finished,
            duration_ms=cycle.context.get("total_duration_ms", 0.0),
            config_hash=None,
            inputs={
                "engine": "aca",
                "objective": cycle.objective,
                "model_provider": cycle.model_provider,
                "layers_completed": [l.value for l in cycle.layers_completed],
            },
            environment=capture_environment(),
            evidence_tier={"aggregate": "measured", "layers": len(cycle.layers_completed)},
            runtime={"sme_session_id": cycle.sme_session_id},
        )
        get_provenance_store(self.db_path).save(record)

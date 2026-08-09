"""Verification Factory orchestrator — continuous verify loop (VF §27)."""

from __future__ import annotations

import logging
import subprocess
from typing import Any

from axiom.config import settings
from axiom.vfactory.journeys import ALL_JOURNEYS
from axiom.vfactory.models import (
    JourneyResult,
    TestLevel,
    TestRunResult,
    VerificationRun,
    _new_id,
)
from axiom.vfactory.pyramid import (
    LOOP_HEALTH_CHECKS,
    run_health_check,
    run_scientific_benchmark,
    run_security_scan,
    run_static_analysis,
    run_unit_tests,
)
from axiom.vfactory.registry import seed_registry, update_capability_status
from axiom.vfactory.scorer import compute_all_scores
from axiom.vfactory.store import VFactoryStore, get_vfactory_store

logger = logging.getLogger(__name__)


class VFactoryOrchestrator:
    """Coordinates verification pyramid, journeys, and registry updates."""

    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or settings.db_path
        self.store = get_vfactory_store(self.db_path)

    def bootstrap(self) -> dict[str, Any]:
        """Seed registry and return current state."""
        caps = seed_registry(self.store)
        scores = compute_all_scores(caps)
        overall = next((s for s in scores if s.domain.value == "overall"), None)
        return {
            "capabilities_seeded": len(caps),
            "overall_score": overall.score if overall else 0.0,
            "domains": [s.to_dict() for s in scores],
        }

    def run_pyramid_level(self, level: TestLevel) -> TestRunResult:
        """Run a single pyramid level."""
        if level == TestLevel.STATIC_ANALYSIS:
            result = run_static_analysis()
        elif level == TestLevel.UNIT:
            result = run_unit_tests()
        elif level == TestLevel.SECURITY:
            result = run_security_scan()
        elif level == TestLevel.SCIENTIFIC:
            result = run_scientific_benchmark("scripts/fmtp_health_check.py")
        else:
            result = TestRunResult(
                run_id=_new_id("trun"),
                level=level,
                test_name=f"level_{level.name}",
                passed=False,
                duration_seconds=0.0,
                error=f"Level {level.name} not yet automated",
            )
        self.store.save_test_run(result)
        return result

    def run_health_gates(self) -> list[TestRunResult]:
        """Run loop health checks as component/integration gates."""
        results: list[TestRunResult] = []
        for target in LOOP_HEALTH_CHECKS:
            result = run_health_check(target)
            self.store.save_test_run(result)
            results.append(result)
        return results

    def run_journey(self, journey_key: str) -> JourneyResult:
        """Execute a single user journey."""
        fn = ALL_JOURNEYS.get(journey_key)
        if not fn:
            raise ValueError(f"Unknown journey: {journey_key}")
        result = fn(":memory:")
        self.store.save_journey(result)
        return result

    def run_all_journeys(self) -> list[JourneyResult]:
        """Execute all user journey tests."""
        results = [fn(":memory:") for fn in ALL_JOURNEYS.values()]
        for jr in results:
            self.store.save_journey(jr)
        return results

    def discover_affected_capabilities(self, changed_paths: list[str] | None = None) -> list[str]:
        """Map changed files to capability IDs."""
        caps = self.store.list_capabilities()
        if not changed_paths:
            return [c.capability_id for c in caps]

        affected: set[str] = set()
        for path in changed_paths:
            for cap in caps:
                if any(sp in path for sp in cap.source_paths):
                    affected.add(cap.capability_id)
        return list(affected) or ["cap_api_gateway"]

    def run_verification_cycle(
        self,
        *,
        run_pyramid: bool = True,
        run_journeys: bool = True,
        run_health: bool = False,
        changed_paths: list[str] | None = None,
    ) -> VerificationRun:
        """Full verification cycle: discover → test → score → update registry."""
        run_id = _new_id("vrun")
        results: list[dict[str, Any]] = []
        failures: list[str] = []

        affected = self.discover_affected_capabilities(changed_paths)
        seed_registry(self.store)

        if run_pyramid:
            for level in (TestLevel.STATIC_ANALYSIS, TestLevel.UNIT, TestLevel.SECURITY):
                tr = self.run_pyramid_level(level)
                results.append(tr.to_dict())
                if not tr.passed:
                    failures.append(f"{tr.test_name}: {tr.error or 'failed'}")

        if run_health:
            for tr in self.run_health_gates():
                results.append(tr.to_dict())
                if not tr.passed:
                    failures.append(f"{tr.test_name}: {tr.error or 'failed'}")

        journey_results: list[JourneyResult] = []
        if run_journeys:
            journey_results = self.run_all_journeys()
            for jr in journey_results:
                results.append(jr.to_dict())
                if not jr.passed:
                    failed_steps = [s["step"] for s in jr.step_results if not s["passed"]]
                    failures.append(f"{jr.journey_name}: {', '.join(failed_steps)}")

        self._update_registry(results, journey_results)
        scores = compute_all_scores(self.store.list_capabilities())
        overall_passed = len(failures) == 0

        commit: str | None = None
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=5,
            )
            if proc.returncode == 0:
                commit = proc.stdout.strip()
        except Exception:
            pass

        vrun = VerificationRun(
            verification_run_id=run_id,
            commit=commit,
            version=settings.app_version,
            environment=settings.environment,
            configuration={
                "run_pyramid": run_pyramid,
                "run_journeys": run_journeys,
                "run_health": run_health,
                "affected_capabilities": affected,
            },
            results=results,
            scores=[s.to_dict() for s in scores],
            overall_passed=overall_passed,
            failures=failures,
        )
        self.store.save_verification_run(vrun)
        return vrun

    def _update_registry(
        self,
        pyramid_and_journey: list[dict[str, Any]],
        journeys: list[JourneyResult],
    ) -> None:
        """Sync registry status from test outcomes."""
        level_cap_map = {
            int(TestLevel.STATIC_ANALYSIS): "cap_api_gateway",
            int(TestLevel.UNIT): "cap_api_gateway",
            int(TestLevel.SECURITY): "cap_tss",
        }
        for item in pyramid_and_journey:
            if "level" in item:
                cap_id = level_cap_map.get(item["level"], "cap_api_gateway")
                update_capability_status(
                    self.store, cap_id,
                    passed=item.get("passed", False),
                    evidence_id=item.get("run_id", _new_id("ev")),
                )

        journey_cap_map = {
            "Journey A: Research Workspace": "cap_research_ws",
            "Journey B: Research Campaign": "cap_frce",
            "Journey C: Formal Mathematics": "cap_fmtp",
            "Journey D: Sandbox Recovery": "cap_sec",
        }
        for jr in journeys:
            cap_id = journey_cap_map.get(jr.journey_name, "cap_api_gateway")
            update_capability_status(
                self.store, cap_id,
                passed=jr.passed,
                evidence_id=jr.journey_id,
            )

    def get_status(self) -> dict[str, Any]:
        """Current verification status snapshot."""
        caps = seed_registry(self.store)
        scores = compute_all_scores(caps)
        latest = self.store.get_latest_verification_run()
        return {
            "scores": [s.to_dict() for s in scores],
            "capabilities": [c.to_dict() for c in caps],
            "latest_run": latest.to_dict() if latest else None,
            "recent_test_runs": [t.to_dict() for t in self.store.list_test_runs(limit=10)],
        }

    def get_run(self, run_id: str) -> VerificationRun | None:
        return self.store.get_verification_run(run_id)

    @property
    def registry_store(self) -> VFactoryStore:
        return self.store

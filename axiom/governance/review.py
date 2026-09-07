"""Engineering review orchestrator."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from axiom.governance.collectors import run_all_collectors
from axiom.governance.collectors.performance import save_performance_baseline
from axiom.governance.council import run_council_review
from axiom.governance.models import GovernanceSnapshot
from axiom.governance.reports import (
    generate_dashboard_json,
    generate_engineering_health,
    generate_product_health,
    generate_research_health,
    generate_tech_debt_board,
    generate_top_25_priorities,
)
from axiom.governance.scoring import build_priorities, compute_scores, select_top_initiative


class EngineeringReview:
    """Run a full engineering governance cycle and write reports."""

    REPORT_FILES: ClassVar[dict] = {
        "ENGINEERING_HEALTH.md": generate_engineering_health,
        "PRODUCT_HEALTH.md": generate_product_health,
        "RESEARCH_HEALTH.md": generate_research_health,
        "TECH_DEBT_BOARD.md": generate_tech_debt_board,
        "TOP_25_PRIORITIES.md": generate_top_25_priorities,
    }

    def __init__(self, workspace_root: str | Path = "."):
        self.workspace = Path(workspace_root).resolve()

    def run(self, *, update_baseline: bool = False) -> GovernanceSnapshot:
        timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        snapshot = GovernanceSnapshot(
            timestamp=timestamp,
            workspace_root=str(self.workspace),
        )

        snapshot.collectors = run_all_collectors(self.workspace)
        compute_scores(snapshot)
        run_council_review(snapshot)
        build_priorities(snapshot)
        select_top_initiative(snapshot)

        if update_baseline:
            perf = snapshot.collectors.get("performance")
            if perf and "cold_import_ms" in perf.raw:
                save_performance_baseline(self.workspace, perf.raw["cold_import_ms"])

        return snapshot

    def write_reports(self, snapshot: GovernanceSnapshot | None = None) -> dict[str, Path]:
        if snapshot is None:
            snapshot = self.run()

        written: dict[str, Path] = {}
        for filename, generator in self.REPORT_FILES.items():
            path = self.workspace / filename
            path.write_text(generator(snapshot), encoding="utf-8")
            written[filename] = path

        dashboard_dir = self.workspace / ".axiom" / "governance"
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        dashboard_path = dashboard_dir / "dashboard.json"
        dashboard_path.write_text(generate_dashboard_json(snapshot), encoding="utf-8")
        written[".axiom/governance/dashboard.json"] = dashboard_path

        snapshot_path = dashboard_dir / "last_snapshot.json"
        snapshot_path.write_text(
            json.dumps(
                {
                    "timestamp": snapshot.timestamp,
                    "scores": snapshot.scores.as_dict(),
                    "top_initiative": snapshot.top_initiative,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        written[".axiom/governance/last_snapshot.json"] = snapshot_path

        return written

    def run_and_write(self, *, update_baseline: bool = False) -> GovernanceSnapshot:
        snapshot = self.run(update_baseline=update_baseline)
        self.write_reports(snapshot)
        return snapshot

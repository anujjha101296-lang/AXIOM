"""Tests for AXIOM Operating System governance artifacts."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AXIOM_DIR = REPO_ROOT / ".axiom"


class TestOperatingSystem:
    def test_core_os_files_exist(self):
        required = [
            REPO_ROOT / "AXIOM_OPERATING_SYSTEM.md",
            AXIOM_DIR / "OPERATING_SYSTEM.md",
            AXIOM_DIR / "CONSTITUTION.md",
            AXIOM_DIR / "NORTH_STAR_METRICS.md",
            AXIOM_DIR / "REPOSITORY_MAP.md",
            AXIOM_DIR / "templates" / "MONTHLY_STRATEGIC_REVIEW.md",
        ]
        for path in required:
            assert path.exists(), f"Missing OS artifact: {path}"

    def test_seven_layers_documented(self):
        content = (AXIOM_DIR / "OPERATING_SYSTEM.md").read_text()
        for i in range(1, 8):
            assert f"Layer {i}" in content

    def test_agents_entry_points_to_os(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text()
        assert "OPERATING_SYSTEM.md" in agents
        assert "Continuous Evolution Loop" in agents

    def test_constitution_read_order(self):
        constitution = (AXIOM_DIR / "CONSTITUTION.md").read_text()
        assert "OPERATING_SYSTEM.md" in constitution
        assert "Prompt completion is not organizational progress" in constitution

    def test_north_star_anti_metrics(self):
        metrics = (AXIOM_DIR / "NORTH_STAR_METRICS.md").read_text()
        assert "Lines of code" in metrics
        assert "unavailable" in metrics

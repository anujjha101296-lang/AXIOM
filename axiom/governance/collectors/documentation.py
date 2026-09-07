"""Documentation coverage analysis."""

from __future__ import annotations

from pathlib import Path

from axiom.governance.models import (
    CollectorResult,
    Finding,
    FindingCategory,
    MetricValue,
    Severity,
)

REQUIRED_ROOT_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "ARCHITECTURE.md",
    "ENGINEERING.md",
)

REQUIRED_DOCS_DIR = (
    "docs/api.md",
    "docs/architecture.md",
)


def collect_documentation(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="documentation")
    md_files = [p for p in workspace.rglob("*.md") if ".git" not in p.parts and "node_modules" not in p.parts]
    result.metrics.append(MetricValue("markdown_files", len(md_files), unit="count"))

    missing_root = [d for d in REQUIRED_ROOT_DOCS if not (workspace / d).exists()]
    missing_docs = [d for d in REQUIRED_DOCS_DIR if not (workspace / d).exists()]
    result.metrics.append(MetricValue("missing_required_docs", len(missing_root) + len(missing_docs), target=0))

    for doc in missing_root + missing_docs:
        result.findings.append(
            Finding(
                category=FindingCategory.DOCUMENTATION,
                severity=Severity.MEDIUM,
                title=f"Missing required doc: {doc}",
                detail="Contributor and architecture docs must exist.",
                recommendation=f"Author {doc} or restore from main branch",
                source=doc,
                score_impact=2.0,
            )
        )

    docstring_ratio = _docstring_coverage(workspace / "axiom")
    result.metrics.append(
        MetricValue(
            "module_docstring_coverage_pct",
            round(docstring_ratio * 100, 1),
            unit="%",
            target=60,
            status="ok" if docstring_ratio >= 0.5 else "warn",
        )
    )
    if docstring_ratio < 0.4:
        result.findings.append(
            Finding(
                category=FindingCategory.DOCUMENTATION,
                severity=Severity.LOW,
                title="Low module docstring coverage",
                detail=f"Only {docstring_ratio*100:.0f}% of axiom modules have module docstrings",
                recommendation="Add module-level docstrings to public packages",
                source="axiom/",
                score_impact=1.0,
            )
        )

    api_doc = workspace / "docs" / "api.md"
    main_py = workspace / "axiom" / "services" / "api_gateway" / "main.py"
    if api_doc.exists() and main_py.exists():
        route_count = main_py.read_text().count("@app.")
        api_text = api_doc.read_text(encoding="utf-8", errors="ignore")
        if route_count > 5 and api_text.count("##") < 5:
            result.findings.append(
                Finding(
                    category=FindingCategory.DOCUMENTATION,
                    severity=Severity.MEDIUM,
                    title="API documentation may be stale",
                    detail="main.py has many routes but docs/api.md has few sections",
                    recommendation="Sync docs/api.md with mounted routers",
                    source="docs/api.md",
                    score_impact=2.0,
                )
            )

    result.raw["docstring_ratio"] = docstring_ratio
    return result


def _docstring_coverage(package_dir: Path) -> float:
    if not package_dir.exists():
        return 0.0
    modules = [p for p in package_dir.rglob("*.py") if p.name != "__init__.py"]
    if not modules:
        return 0.0
    documented = 0
    for path in modules:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        stripped = text.lstrip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            documented += 1
    return documented / len(modules)

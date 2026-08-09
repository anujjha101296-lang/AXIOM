"""Repository secret pattern scanner (TSS §12)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".next",
    "__pycache__",
    ".reports",
    "data",
}

DEFAULT_SKIP_FILES = {
    ".env.example",
    "SECRET_SCAN_ALLOWLIST",
}

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("jwt_like", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.")),
)


@dataclass
class SecretMatch:
    path: str
    line: int
    kind: str
    snippet: str


def scan_repository_for_secrets(
    root: Path,
    *,
    skip_dirs: set[str] | None = None,
) -> list[SecretMatch]:
    """Scan tracked-like source files for obvious secret patterns."""
    skip = skip_dirs or DEFAULT_SKIP_DIRS
    matches: list[SecretMatch] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip for part in path.parts):
            continue
        if path.name in DEFAULT_SKIP_FILES:
            continue
        if path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".db", ".sqlite"}:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            if "CHANGE-ME" in line or "axiom-dev-token" in line:
                continue  # documented placeholders
            for kind, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    matches.append(
                        SecretMatch(
                            path=str(path.relative_to(root)),
                            line=line_no,
                            kind=kind,
                            snippet=line.strip()[:120],
                        )
                    )
    return matches

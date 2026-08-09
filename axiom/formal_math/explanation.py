"""Formal → informal explanation pipeline (FMTP §4)."""

from __future__ import annotations

import re


def explain_formal_artifact(
    formal_spec: str,
    *,
    theorem_name: str = "theorem",
    compilation_status: str = "unknown",
) -> str:
    """Generate human-readable explanation linked to formal artifact.

    Must not introduce claims not present in the verified formal result.
    """
    lines = []
    lines.append(f"Formal artifact: {theorem_name}")
    lines.append(f"Verification status: {compilation_status}")

    theorem_match = re.search(r"theorem\s+(\w+)", formal_spec)
    if theorem_match:
        lines.append(f"Identifier: {theorem_match.group(1)}")

    if ":=" in formal_spec:
        statement_part = formal_spec.split(":=")[0]
        if ":" in statement_part:
            stmt = statement_part.split(":", 1)[-1].strip()
            lines.append(f"Statement (from formal source): {stmt}")

    if "sorry" in formal_spec:
        lines.append(
            "Note: Proof body contains 'sorry' — this is NOT formally verified. "
            "The statement is specified but not machine-checked."
        )
    elif compilation_status == "FORMALLY_VERIFIED":
        lines.append(
            "This result was accepted by the theorem prover. "
            "Explanation is derived only from the verified formal artifact."
        )
    else:
        lines.append(
            "This explanation reflects the formal specification only. "
            "No additional mathematical claims are introduced."
        )

    imports = re.findall(r"^import\s+(\S+)", formal_spec, re.MULTILINE)
    if imports:
        lines.append(f"Dependencies (imports): {', '.join(imports[:5])}")

    return "\n".join(lines)

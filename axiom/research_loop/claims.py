"""Claim classification utilities for research loop outputs."""

from __future__ import annotations

import re
from typing import List

from axiom.research_loop.schema import ClaimStatus, EvidenceItem, ResearchClaim


def classify_claim(statement: str, evidence: List[EvidenceItem], verified: bool = False) -> ClaimStatus:
    if verified:
        return ClaimStatus.FORMALLY_VERIFIED
    lower = statement.lower()
    if any(w in lower for w in ("disproved", "refuted", "counterexample", "false")):
        return ClaimStatus.DISPROVED
    if any(w in lower for w in ("proven", "theorem", "qed", "formally verified")):
        if evidence:
            return ClaimStatus.SUPPORTED
        return ClaimStatus.SPECULATIVE
    if evidence:
        return ClaimStatus.SUPPORTED
    if any(w in lower for w in ("conjecture", "might", "possibly", "perhaps", "hypothesis")):
        return ClaimStatus.SPECULATIVE
    if any(w in lower for w in ("known", "classical", "established", "well-known")):
        return ClaimStatus.KNOWN
    return ClaimStatus.UNVERIFIED


def extract_numeric_claims(text: str) -> List[str]:
    patterns = [
        r"\d+\s*\+\s*\d+\s*=\s*\d+",
        r"n\s*\(\s*n\s*\+\s*1\s*\)\s*/\s*2",
        r"V\s*-\s*E\s*\+\s*F\s*=\s*2",
        r"\d+\^2\s*\+\s*\d+\^2\s*=\s*\d+\^2",
    ]
    found: list[str] = []
    for pat in patterns:
        found.extend(re.findall(pat, text, re.IGNORECASE))
    return found


def claim_from_statement(
    statement: str,
    evidence: List[EvidenceItem],
    iteration: int,
    provenance: str,
    verified: bool = False,
) -> ResearchClaim:
    status = classify_claim(statement, evidence, verified=verified)
    return ResearchClaim(
        statement=statement,
        status=status,
        evidence_ids=[e.id for e in evidence[:3]],
        confidence=0.9 if status == ClaimStatus.FORMALLY_VERIFIED else 0.6 if status == ClaimStatus.SUPPORTED else 0.3,
        iteration=iteration,
        provenance=provenance,
    )

"""
axiom.long_horizon.memory
=========================
Approach Memory Engine.
Prevents duplicate rediscovery of previously failed proof strategies or assumptions.
"""
from __future__ import annotations

import hashlib
import re
from typing import Optional, Tuple

from axiom.long_horizon.models import ApproachMemory, ApproachStatus


class ApproachMemoryEngine:
    """Manages approach memory and prevents repeating failed strategies."""

    def compute_approach_hash(self, method: str, approach_description: str) -> str:
        """Compute canonical hash of an approach."""
        clean_text = f"{method.lower().strip()}:{re.sub(r'[^a-zA-Z0-9]', '', approach_description.lower())}"
        return hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:16]

    def check_duplicate_attempt(
        self,
        existing_memories: list[ApproachMemory],
        method: str,
        approach_description: str,
    ) -> Tuple[bool, Optional[ApproachMemory]]:
        """
        Check if approach matches a previously failed or falsified attempt.
        Returns (is_duplicate, matching_memory).
        """
        app_hash = self.compute_approach_hash(method, approach_description)
        for mem in existing_memories:
            if mem.approach_hash == app_hash or (method.lower() in mem.summary.lower() and mem.status in (ApproachStatus.FAILED, ApproachStatus.FALSIFIED)):
                return True, mem
        return False, None

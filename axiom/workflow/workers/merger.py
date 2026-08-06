"""
AXIOM Workflow Engine — MergerWorker
======================================
Combines outputs from N parallel worker tasks into a unified artifact.
Handles deduplication, conflict detection, and structured merging.
"""
from __future__ import annotations

import logging
from collections import Counter

from .base import BaseWorker
from ..models import Task, WorkflowContext, WorkerResult, ArtifactType, Artifact
from ..memory import WorkflowMemory

logger = logging.getLogger(__name__)


class MergerWorker(BaseWorker):
    """
    Merges accumulated knowledge from multiple parallel tasks into one artifact.

    Reads from working memory:
        knowledge:claims    → list[str]
        knowledge:concepts  → list[str]

    Deduplication:
        - Exact duplicate claims removed
        - Concept frequency tracked; top concepts ranked

    Output:
        outputs["merged_claims"]   = list[str] (deduplicated)
        outputs["merged_concepts"] = list[str] (ranked by frequency)
        outputs["source_count"]    = int
        outputs["claim_count"]     = int
    """

    worker_type = "merger"
    mission = "Combine outputs from multiple parallel tasks into a unified, deduplicated knowledge object"
    capabilities = ["deduplication", "knowledge_merging", "conflict_detection", "synthesis"]

    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> WorkerResult:
        # Pull accumulated knowledge from working memory
        all_claims: list[str] = await memory.get_accumulated_knowledge("claims")
        all_concepts: list[str] = await memory.get_accumulated_knowledge("concepts")

        # Also accept direct inputs (for non-memory-based pipelines)
        direct_claims = task.inputs.get("claims", [])
        direct_concepts = task.inputs.get("key_concepts", [])
        if direct_claims:
            all_claims = list(all_claims) + list(direct_claims)
        if direct_concepts:
            all_concepts = list(all_concepts) + list(direct_concepts)

        source_count = int(task.inputs.get("source_count", 1))

        # Deduplicate claims (preserve order, remove exact duplicates)
        seen: set[str] = set()
        merged_claims: list[str] = []
        for claim in all_claims:
            claim_norm = claim.strip().lower()
            if claim_norm not in seen and claim.strip():
                seen.add(claim_norm)
                merged_claims.append(claim.strip())

        # Rank concepts by frequency
        concept_freq = Counter(c.lower().strip() for c in all_concepts if c.strip())
        ranked_concepts = [c for c, _ in concept_freq.most_common(20)]

        # Detect potential conflicts (claims containing "not" vs similar claims)
        conflicts = self._detect_conflicts(merged_claims)

        # Store merged result back to working memory
        await memory.set("merged_claims", merged_claims, source_task_id=task.id)
        await memory.set("merged_concepts", ranked_concepts, source_task_id=task.id)
        if conflicts:
            for conflict in conflicts:
                await memory.add_open_question(conflict, source_task_id=task.id)

        merged_artifact = Artifact(
            task_id=task.id,
            workflow_id=task.workflow_id,
            artifact_type=ArtifactType.KNOWLEDGE_OBJECT,
            title=f"Merged Knowledge: {context.objective[:60]}",
            content={
                "merged_claims": merged_claims,
                "merged_concepts": ranked_concepts,
                "source_count": source_count,
                "original_claim_count": len(all_claims),
                "duplicate_claims_removed": len(all_claims) - len(merged_claims),
                "conflicts_detected": conflicts,
            },
            text_content=self._format_merged(
                context.objective, merged_claims, ranked_concepts, conflicts, source_count
            ),
        )

        logger.info(
            f"MergerWorker: merged {len(all_claims)} claims → {len(merged_claims)} unique, "
            f"{len(ranked_concepts)} concepts, {len(conflicts)} conflicts"
        )

        return WorkerResult(
            success=True,
            outputs={
                "merged_claims": merged_claims,
                "merged_concepts": ranked_concepts,
                "source_count": source_count,
                "claim_count": len(merged_claims),
                "conflicts": conflicts,
            },
            artifacts=[merged_artifact],
        )

    def _detect_conflicts(self, claims: list[str]) -> list[str]:
        """
        Simple heuristic conflict detection.
        v1: flags pairs where one claim contains 'not' version of another.
        v2: will use semantic similarity.
        """
        conflicts = []
        for i, claim_a in enumerate(claims):
            for claim_b in claims[i + 1:]:
                # Check if one negates key words in the other
                words_a = set(claim_a.lower().split())
                words_b = set(claim_b.lower().split())
                shared = words_a & words_b
                if len(shared) > 3:
                    a_has_not = "not" in words_a or "no" in words_a
                    b_has_not = "not" in words_b or "no" in words_b
                    if a_has_not != b_has_not:
                        conflicts.append(
                            f"Potential conflict: {claim_a[:60]!r} vs {claim_b[:60]!r}"
                        )
        return conflicts[:5]  # Cap at 5 conflict reports

    def _format_merged(
        self,
        objective: str,
        claims: list[str],
        concepts: list[str],
        conflicts: list[str],
        source_count: int,
    ) -> str:
        lines = [
            f"# Merged Knowledge Object",
            f"Objective: {objective}",
            f"Sources merged: {source_count}",
            f"Unique claims: {len(claims)}",
            "",
            "## Merged Claims",
            *[f"- {c}" for c in claims],
            "",
            "## Top Concepts (by frequency)",
            *[f"- {c}" for c in concepts],
        ]
        if conflicts:
            lines += ["", "## Conflicts Detected", *[f"⚠️ {c}" for c in conflicts]]
        return "\n".join(lines)

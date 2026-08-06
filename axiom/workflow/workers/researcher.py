"""
AXIOM Workflow Engine — ResearchWorker
========================================
Reads a source (URL, text, or topic) and extracts structured knowledge.
v1: Deterministic structured extraction from provided text/inputs.
v2: Will use LLM-backed reading and semantic extraction.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime

from .base import BaseWorker
from ..models import Task, WorkflowContext, WorkerResult, ArtifactType, Artifact, FailureAction
from ..memory import WorkflowMemory

logger = logging.getLogger(__name__)


class ResearchWorker(BaseWorker):
    """
    Reads a source and extracts structured knowledge.

    Inputs (any of):
        - source_url: URL to read
        - source_text: Raw text to extract from
        - topic: Topic string (generates stub claims in v1)
        - objective: Fallback — extract from objective statement

    Output:
        outputs["claims"]       = list[str]
        outputs["key_concepts"] = list[str]
        outputs["source"]       = str
        outputs["word_count"]   = int
    """

    worker_type = "researcher"
    mission = "Read a source and extract key claims, concepts, and findings"
    capabilities = ["text_reading", "claim_extraction", "concept_identification", "literature_review"]

    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> WorkerResult:
        inputs = task.inputs

        # Determine source text
        source_text = inputs.get("source_text", "")
        source_url = inputs.get("source_url", "")
        topic = inputs.get("topic", inputs.get("objective", context.objective))

        if source_url and not source_text:
            # v2: will fetch and parse URL
            source_text = f"[Source: {source_url}]\n(URL reading will be implemented in v2)"
            logger.info(f"ResearchWorker: URL reading stub for {source_url}")

        if not source_text:
            # Generate synthetic research stub from topic (v1 fallback)
            source_text = self._generate_stub(topic, context.domain)

        # Extract structured knowledge
        claims = self._extract_claims(source_text, topic)
        concepts = self._extract_concepts(source_text, topic)
        summary = self._summarize(source_text, topic)

        # Accumulate into working memory
        for claim in claims:
            await memory.accumulate_knowledge("claims", claim, source_task_id=task.id)
        for concept in concepts:
            await memory.accumulate_knowledge("concepts", concept, source_task_id=task.id)

        artifact = Artifact(
            task_id=task.id,
            workflow_id=task.workflow_id,
            artifact_type=ArtifactType.RESEARCH_NOTE,
            title=f"Research: {topic[:60]}",
            content={
                "claims": claims,
                "key_concepts": concepts,
                "summary": summary,
                "source": source_url or "generated_stub",
                "extracted_at": datetime.utcnow().isoformat(),
            },
            text_content=self._format_note(topic, claims, concepts, summary),
        )

        logger.info(
            f"ResearchWorker: extracted {len(claims)} claims, {len(concepts)} concepts "
            f"from {source_url or 'stub'!r}"
        )

        return WorkerResult(
            success=True,
            outputs={
                "claims": claims,
                "key_concepts": concepts,
                "summary": summary,
                "source": source_url or "stub",
                "word_count": len(source_text.split()),
            },
            artifacts=[artifact],
        )

    def _generate_stub(self, topic: str, domain: str) -> str:
        """Generate a plausible research stub for v1 demo purposes."""
        return f"""
Research on: {topic}

Domain: {domain}

Overview:
This research note covers the key aspects of {topic}.
The subject has been studied extensively in recent literature.

Key Findings:
1. The core mechanism involves structured knowledge representation.
2. Recent advances have shown significant improvements in automated reasoning.
3. Evaluation frameworks are essential for measuring progress objectively.
4. Reproducibility requires formal verification of key claims.
5. Open problems remain in the areas of scalability and generalization.

Methods:
Standard experimental methods were applied across multiple benchmarks.

Conclusion:
The area of {topic} remains an active research frontier with substantial open problems.
        """.strip()

    def _extract_claims(self, text: str, topic: str) -> list[str]:
        """Extract claim statements from text. v1: sentence-based heuristic."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claim_indicators = [
            "show", "demonstrat", "find", "found", "result", "conclude",
            "suggest", "propos", "introduc", "present", "establish",
            "claim", "prove", "verif", "confirm", "reveal",
        ]
        claims = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20:
                continue
            lower = sent.lower()
            if any(ind in lower for ind in claim_indicators):
                claims.append(sent)
        # Fallback: take first 3 substantive sentences
        if not claims:
            claims = [s.strip() for s in sentences if len(s.strip()) > 40][:3]
        return claims[:8]  # Cap at 8 claims per source

    def _extract_concepts(self, text: str, topic: str) -> list[str]:
        """Extract key concept terms. v1: topic-word extraction."""
        # Strip topic words and common stop words
        stop = {"the", "a", "an", "is", "in", "of", "and", "or", "to", "for",
                "with", "on", "at", "by", "from", "as", "be", "are", "was"}
        words = re.findall(r'\b[A-Za-z][a-z]+\b', text)
        freq: dict[str, int] = {}
        for w in words:
            wl = w.lower()
            if wl not in stop and len(wl) > 4:
                freq[wl] = freq.get(wl, 0) + 1
        sorted_words = sorted(freq, key=lambda k: freq[k], reverse=True)
        # Include topic words as concepts
        topic_words = [w for w in topic.split() if len(w) > 3]
        concepts = list(dict.fromkeys(topic_words + sorted_words))
        return concepts[:10]

    def _summarize(self, text: str, topic: str) -> str:
        """v1 summarize: first 2 substantive sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        substantive = [s.strip() for s in sentences if len(s.strip()) > 40]
        return " ".join(substantive[:2]) if substantive else f"Research note on: {topic}"

    def _format_note(
        self, topic: str, claims: list[str], concepts: list[str], summary: str
    ) -> str:
        lines = [
            f"# Research Note: {topic}",
            "",
            f"## Summary\n{summary}",
            "",
            "## Key Claims",
            *[f"- {c}" for c in claims],
            "",
            "## Key Concepts",
            *[f"- {c}" for c in concepts],
        ]
        return "\n".join(lines)

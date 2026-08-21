"""Document summarization using the model gateway with extractive fallback."""

from __future__ import annotations

from axiom.observability.logger import get_logger
from axiom.services.model_gateway.client import ModelClient

logger = get_logger(__name__)

MAX_SUMMARY_INPUT_CHARS = 12000


class DocumentSummarizer:
    """Generate summaries from extracted document text."""

    def __init__(self, model_client: ModelClient | None = None):
        self.model_client = model_client or ModelClient()

    def summarize(self, text: str, title: str = "document") -> str:
        if not text or not text.strip():
            raise ValueError("Cannot summarize empty document text")

        trimmed = text.strip()
        if len(trimmed) > MAX_SUMMARY_INPUT_CHARS:
            trimmed = trimmed[:MAX_SUMMARY_INPUT_CHARS] + "\n...[truncated]"

        prompt = (
            f"Summarize the following research document titled '{title}' for a scientist. "
            "Include: (1) main thesis, (2) key methods, (3) principal findings, "
            "(4) limitations. Be factual and concise (150-250 words).\n\n"
            f"DOCUMENT:\n{trimmed}"
        )

        try:
            summary = self.model_client.generate(prompt, temperature=0.3)
            if summary and len(summary.strip()) >= 40:
                logger.info("Document summary generated", extra={"title": title, "chars": len(summary)})
                return summary.strip()
        except Exception as exc:
            logger.warning("Model summary failed, using extractive fallback", extra={"error": str(exc)})

        return self._extractive_summary(trimmed, title)

    def _extractive_summary(self, text: str, title: str) -> str:
        """Simple extractive fallback when no LLM is available."""
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
        lead = paragraphs[0] if paragraphs else text[:500]
        excerpt = paragraphs[1][:300] if len(paragraphs) > 1 else ""
        summary = f"Summary of '{title}': {lead}"
        if excerpt:
            summary += f" Additional context: {excerpt}"
        summary += (
            " [Extractive summary — configure OPENAI_API_KEY or GEMINI_API_KEY for LLM summaries.]"
        )
        logger.info("Extractive summary generated", extra={"title": title})
        return summary[:2000]

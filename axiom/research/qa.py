"""Question-answering over uploaded research documents."""

from __future__ import annotations

import re
from typing import List, Tuple

from axiom.observability.logger import get_logger
from axiom.research.schema import ResearchDocument
from axiom.routing.selector import route_task
from axiom.services.model_gateway.client import ModelClient

logger = get_logger(__name__)

MAX_CONTEXT_CHARS = 10000


class PaperQA:
    """Answer questions using document text and the model gateway."""

    def __init__(self, model_client: ModelClient | None = None):
        self.model_client = model_client or ModelClient()

    def answer(
        self,
        question: str,
        documents: List[ResearchDocument],
    ) -> Tuple[str, List[str]]:
        if not question.strip():
            raise ValueError("Question cannot be empty")
        if not documents:
            raise ValueError("No documents available to answer from")

        context, sources = self._build_context(documents)
        prompt = (
            "You are a research assistant. Answer the question using ONLY the document context below. "
            "If the context does not contain enough information, say so clearly. "
            "Cite document filenames when relevant.\n\n"
            f"DOCUMENT CONTEXT:\n{context}\n\n"
            f"QUESTION: {question.strip()}\n\n"
            "ANSWER:"
        )

        try:
            routing = route_task(
                f"Literature Q&A: {question.strip()}",
            )
            model = routing.selected_model
            answer = self.model_client.generate(prompt, model=model, temperature=0.2)
            if answer and len(answer.strip()) >= 20:
                logger.info(
                    "Paper Q&A answered",
                    extra={"question_len": len(question), "source_count": len(sources)},
                )
                return answer.strip(), sources
        except Exception as exc:
            logger.warning("Model Q&A failed, using extractive fallback", extra={"error": str(exc)})

        return self._extractive_answer(question, documents), sources

    def _build_context(self, documents: List[ResearchDocument]) -> Tuple[str, List[str]]:
        parts: List[str] = []
        sources: List[str] = []
        remaining = MAX_CONTEXT_CHARS

        for doc in documents:
            text = doc.summary.strip() or doc.text_content.strip()
            if not text:
                continue
            chunk = text[:remaining]
            if len(text) > remaining:
                chunk += "\n...[truncated]"
            parts.append(f"--- {doc.filename} ---\n{chunk}")
            sources.append(doc.filename)
            remaining -= len(chunk)
            if remaining <= 0:
                break

        return "\n\n".join(parts), sources

    def _extractive_answer(
        self, question: str, documents: List[ResearchDocument]
    ) -> str:
        """Keyword-based fallback when no LLM is available."""
        keywords = [w.lower() for w in re.findall(r"\w+", question) if len(w) > 3]
        if not keywords:
            keywords = [w.lower() for w in re.findall(r"\w+", question)]

        best_sentence = ""
        best_score = 0
        best_source = documents[0].filename

        for doc in documents:
            text = doc.summary or doc.text_content
            for sentence in re.split(r"(?<=[.!?])\s+", text):
                sentence = sentence.strip()
                if len(sentence) < 40:
                    continue
                lower = sentence.lower()
                score = sum(1 for kw in keywords if kw in lower)
                if score > best_score:
                    best_score = score
                    best_sentence = sentence
                    best_source = doc.filename

        if best_sentence:
            return (
                f"Based on '{best_source}': {best_sentence} "
                "[Extractive answer — configure OPENAI_API_KEY or GEMINI_API_KEY for full Q&A.]"
            )

        lead = (documents[0].summary or documents[0].text_content)[:400]
        return (
            f"The uploaded documents may not directly address this question. "
            f"From '{documents[0].filename}': {lead}... "
            "[Extractive fallback — try rephrasing or upload more relevant papers.]"
        )

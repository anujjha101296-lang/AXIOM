"""Question-answering over uploaded research documents."""

from __future__ import annotations

import re
from typing import List, Tuple

from axiom.observability.logger import get_logger
from axiom.research.schema import Citation, ResearchDocument
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
    ) -> Tuple[str, List[str], List[Citation], str, str]:
        """Return answer, source filenames, citations, provider_mode, uncertainty."""
        if not question.strip():
            raise ValueError("Question cannot be empty")
        if not documents:
            raise ValueError("No documents available to answer from")

        context, sources, citations = self._build_context(documents)
        prompt = (
            "You are a research assistant. Answer the question using ONLY the document context below. "
            "If the context does not contain enough information, say so clearly. "
            "Cite document filenames when relevant.\n\n"
            f"DOCUMENT CONTEXT:\n{context}\n\n"
            f"QUESTION: {question.strip()}\n\n"
            "ANSWER:"
        )

        provider_mode = "extractive"
        uncertainty = ""
        try:
            routing = route_task(f"Literature Q&A: {question.strip()}")
            model = routing.selected_model
            answer = self.model_client.generate(prompt, model=model, temperature=0.2)
            if model == "mock-model" or (isinstance(model, str) and "mock" in model.lower()):
                provider_mode = "mock"
                uncertainty = "Response generated without a configured cloud LLM provider."
            else:
                provider_mode = "real"
            if answer and len(answer.strip()) >= 20:
                logger.info(
                    "Paper Q&A answered",
                    extra={
                        "question_len": len(question),
                        "source_count": len(sources),
                        "provider_mode": provider_mode,
                    },
                )
                # Enrich citations with claim snippets from answer context
                for cit in citations:
                    if not cit.claim:
                        cit.claim = cit.snippet[:280]
                return answer.strip(), sources, citations, provider_mode, uncertainty
        except Exception as exc:
            logger.warning("Model Q&A failed, using extractive fallback", extra={"error": str(exc)})
            uncertainty = f"Model unavailable ({exc}); used extractive fallback."

        answer, citations = self._extractive_answer(question, documents)
        return answer, sources, citations, "extractive", uncertainty or "Extractive fallback — configure OPENAI_API_KEY or GEMINI_API_KEY for full Q&A."

    def _build_context(
        self, documents: List[ResearchDocument]
    ) -> Tuple[str, List[str], List[Citation]]:
        parts: List[str] = []
        sources: List[str] = []
        citations: List[Citation] = []
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
            citations.append(
                Citation(
                    document_id=doc.id,
                    filename=doc.filename,
                    snippet=chunk[:400],
                    claim="",
                    evidence_mode="document_extract",
                )
            )
            remaining -= len(chunk)
            if remaining <= 0:
                break

        return "\n\n".join(parts), sources, citations

    def _extractive_answer(
        self, question: str, documents: List[ResearchDocument]
    ) -> Tuple[str, List[Citation]]:
        """Keyword-based fallback when no LLM is available."""
        keywords = [w.lower() for w in re.findall(r"\w+", question) if len(w) > 3]
        if not keywords:
            keywords = [w.lower() for w in re.findall(r"\w+", question)]

        best_sentence = ""
        best_score = 0
        best_doc = documents[0]

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
                    best_doc = doc

        if best_sentence:
            citation = Citation(
                document_id=best_doc.id,
                filename=best_doc.filename,
                snippet=best_sentence[:400],
                claim=best_sentence[:280],
                evidence_mode="document_extract",
            )
            answer = (
                f"Based on '{best_doc.filename}': {best_sentence} "
                "[Extractive answer — configure OPENAI_API_KEY or GEMINI_API_KEY for full Q&A.]"
            )
            return answer, [citation]

        lead = (documents[0].summary or documents[0].text_content)[:400]
        citation = Citation(
            document_id=documents[0].id,
            filename=documents[0].filename,
            snippet=lead,
            claim=lead[:280],
            evidence_mode="document_extract",
        )
        answer = (
            f"The uploaded documents may not directly address this question. "
            f"From '{documents[0].filename}': {lead}... "
            "[Extractive fallback — try rephrasing or upload more relevant papers.]"
        )
        return answer, [citation]

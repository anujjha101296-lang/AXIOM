"""PDF text extraction for research documents."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO

from axiom.observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PdfExtractionResult:
    text: str
    page_count: int


class PdfExtractor:
    """Extract plain text from PDF bytes using pypdf."""

    def extract(self, file_obj: BinaryIO) -> PdfExtractionResult:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            logger.error("pypdf is not installed")
            raise RuntimeError(
                "PDF extraction requires pypdf. Install with: pip install pypdf"
            ) from exc

        try:
            reader = PdfReader(file_obj)
            pages: list[str] = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text.strip())

            combined = "\n\n".join(p for p in pages if p)
            page_count = len(reader.pages)
            logger.info(
                "PDF extracted",
                extra={"pages": page_count, "chars": len(combined)},
            )
            return PdfExtractionResult(text=combined, page_count=page_count)
        except Exception as exc:
            logger.error("PDF extraction failed", extra={"error": str(exc)})
            raise ValueError(f"Failed to extract text from PDF: {exc}") from exc

    def extract_bytes(self, data: bytes) -> PdfExtractionResult:
        return self.extract(BytesIO(data))

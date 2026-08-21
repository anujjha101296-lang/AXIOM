"""Text chunking for document ingestion.

Splits extracted document text into overlapping chunks with configurable
size and stride. Chunk metadata preserves ordering and source boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TextChunk:
    """A single chunk of text with source metadata."""
    chunk_index: int
    content: str
    char_start: int
    char_end: int
    document_id: Optional[str] = None
    project_id: Optional[str] = None
    page_hint: Optional[int] = None  # set if page boundary is detectable


class TextChunker:
    """Split document text into overlapping chunks preserving word boundaries.

    Parameters
    ----------
    chunk_size:
        Target number of characters per chunk (default 500).
    chunk_overlap:
        Number of characters to overlap between consecutive chunks (default 50).
    min_chunk_length:
        Minimum meaningful chunk length. Shorter chunks are discarded (default 20).
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_length: int = 20,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length

    def chunk(
        self,
        text: str,
        document_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[TextChunk]:
        """Split *text* into overlapping chunks and return ordered list.

        Empty or whitespace-only input returns an empty list.
        """
        text = text.strip()
        if not text:
            return []

        # Normalise line-endings and collapse excessive blank lines
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        chunks: List[TextChunk] = []
        stride = self.chunk_size - self.chunk_overlap
        start = 0
        idx = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Snap end to the nearest word boundary to avoid mid-word splits
            if end < len(text):
                snap = text.rfind(" ", start, end)
                if snap > start:
                    end = snap

            raw_chunk = text[start:end].strip()

            if len(raw_chunk) >= self.min_chunk_length:
                chunks.append(
                    TextChunk(
                        chunk_index=idx,
                        content=raw_chunk,
                        char_start=start,
                        char_end=end,
                        document_id=document_id,
                        project_id=project_id,
                    )
                )
                idx += 1

            start += stride

        return chunks

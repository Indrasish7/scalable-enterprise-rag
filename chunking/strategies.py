from abc import ABC, abstractmethod
from typing import List, Dict
import uuid


class BaseChunker(ABC):
    """Abstract base class for all chunking strategies."""

    @abstractmethod
    def chunk(self, documents: List[Dict]) -> List[Dict]:
        pass


class FixedSizeChunker(BaseChunker):
    """
    Splits documents into fixed-size chunks with overlap.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, documents: List[Dict]) -> List[Dict]:
        chunks = []

        for doc in documents:
            text = doc["text"]
            start = 0
            chunk_index = 0

            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]

                if not chunk_text.strip():
                    start = end
                    continue

                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "metadata": {
                        **doc["metadata"],
                        "parent_doc_id": doc["id"],
                        "chunk_index": chunk_index,
                        "chunk_size": len(chunk_text)
                    }
                })

                stride = self.chunk_size - self.overlap
                start += stride
                chunk_index += 1

        return chunks

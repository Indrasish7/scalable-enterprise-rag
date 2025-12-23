from abc import ABC, abstractmethod
from typing import List
import hashlib


class BaseEmbedder(ABC):
    """Abstract base class for embedding models."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass


class DummyEmbedder(BaseEmbedder):
    """
    Placeholder embedder.

    Used for local testing and pipeline validation.
    Replaced later with real embedding models.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = []

        for text in texts:
            # Deterministic pseudo-embedding (for testing)
            hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
            vector = [(hash_value % 1000) / 1000.0] * 128
            embeddings.append(vector)

        return embeddings

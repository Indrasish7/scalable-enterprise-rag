import hashlib
from typing import Dict, List


class EmbeddingCache:
    """
    In-memory embedding cache.

    Maps text hashes → embedding vectors.
    """

    def __init__(self):
        self._cache: Dict[str, List[float]] = {}

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str):
        key = self._hash_text(text)
        return self._cache.get(key)

    def set(self, text: str, embedding: List[float]):
        key = self._hash_text(text)
        self._cache[key] = embedding

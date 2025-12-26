from abc import ABC, abstractmethod
from typing import List
import os
from google import genai


class BaseEmbedder(ABC):
    """Abstract base class for embedding models."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass


class DummyEmbedder(BaseEmbedder):
    """
    Placeholder embedder for testing.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        import hashlib

        embeddings = []
        for text in texts:
            hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
            vector = [(hash_value % 1000) / 1000.0] * 128
            embeddings.append(vector)
        return embeddings


class GeminiEmbedder(BaseEmbedder):
    """
    Production-grade Gemini embedding model.
    """

    def __init__(self, model_name: str = "text-embedding-004"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY not found")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors = []

        for text in texts:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text
            )

            # ✅ Correct attribute access
            vectors.append(response.embeddings[0].values)

        return vectors


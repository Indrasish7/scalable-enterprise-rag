from typing import List, Dict
from embeddings.embedder import BaseEmbedder
from vectorstore.faiss_store import FaissVectorStore


class Retriever:
    """
    Handles semantic retrieval over a vector store.
    """

    def __init__(self, embedder: BaseEmbedder, vector_store: FaissVectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        query_vector = self.embedder.embed([query])[0]
        results = self.vector_store.search(query_vector, top_k=top_k)
        return results

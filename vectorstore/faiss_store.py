import faiss
import numpy as np
from typing import List, Dict


class FaissVectorStore:
    """
    FAISS-based vector store using exact L2 similarity.
    """

    def __init__(self, vector_dim: int):
        self.vector_dim = vector_dim
        self.index = faiss.IndexFlatL2(vector_dim)
        self.metadata: List[Dict] = []

    def add(self, vectors: List[List[float]], metadatas: List[Dict]):
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadata must have same length")

        np_vectors = np.array(vectors).astype("float32")
        self.index.add(np_vectors)
        self.metadata.extend(metadatas)

    def search(self, query_vector: List[float], top_k: int = 5):
        np_query = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(np_query, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue

            results.append({
                "metadata": self.metadata[idx],
                "distance": float(dist)
            })

        return results

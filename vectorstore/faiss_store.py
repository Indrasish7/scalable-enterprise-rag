import faiss
import numpy as np
import os
import pickle
from typing import List, Dict


class FaissVectorStore:
    """
    Persistent FAISS-based vector store using exact L2 similarity.
    """

    def __init__(
        self,
        vector_dim: int,
        index_path: str = "data/faiss.index",
        metadata_path: str = "data/metadata.pkl"
    ):
        self.vector_dim = vector_dim
        self.index_path = index_path
        self.metadata_path = metadata_path

        os.makedirs(os.path.dirname(index_path), exist_ok=True)

        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self._load()
        else:
            self.index = faiss.IndexFlatL2(vector_dim)
            self.metadata: List[Dict] = []

    # -----------------------------
    # Core operations
    # -----------------------------
    def add(self, vectors: List[List[float]], metadatas: List[Dict]):
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadata must have same length")

        np_vectors = np.array(vectors).astype("float32")
        self.index.add(np_vectors)
        self.metadata.extend(metadatas)

        self._save()

    def search(self, query_vector: List[float], top_k: int = 5):
        if self.index.ntotal == 0:
            return []

        np_query = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(np_query, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            results.append({
                "metadata": self.metadata[idx],
                "distance": float(dist)
            })

        return results

    # -----------------------------
    # Persistence
    # -----------------------------
    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def _load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

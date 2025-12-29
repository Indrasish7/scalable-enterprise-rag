import faiss
import numpy as np
import os
import pickle
from typing import List, Dict


class FaissVectorStore:
    def __init__(self, vector_dim: int, persist_dir="/app/data"):
        self.vector_dim = vector_dim
        self.persist_dir = persist_dir
        self.index_path = os.path.join(persist_dir, "faiss.index")
        self.meta_path = os.path.join(persist_dir, "metadata.pkl")

        os.makedirs(persist_dir, exist_ok=True)

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(vector_dim)
            self.metadata: List[Dict] = []

    def add(self, vectors: List[List[float]], metadatas: List[Dict]):
        np_vectors = np.array(vectors).astype("float32")
        self.index.add(np_vectors)
        self.metadata.extend(metadatas)
        self._persist()

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

    def _persist(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

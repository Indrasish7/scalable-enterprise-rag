from typing import List, Dict
from retrieval.retriever import Retriever
from llm.gemini_llm import GeminiLLM
from evaluation.latency import measure_latency


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.
    """

    def __init__(self, retriever: Retriever, llm: GeminiLLM):
        self.retriever = retriever
        self.llm = llm

    def answer(self, query: str, top_k: int = 5) -> str:
        """
        Generate a grounded answer for a user query (simple API).
        """

        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)

        contexts: List[str] = [
            item["metadata"]["text"]
            for item in retrieved_chunks
            if "text" in item["metadata"]
        ]

        # Guard against empty retrieval
        if not contexts:
            return "I don't know based on the provided context."

        contexts = contexts[:top_k]

        return self.llm.generate(query=query, contexts=contexts)

    def answer_with_observability(self, query: str, top_k: int = 5) -> Dict:
        """
        Generate an answer with observability:
        - retrieval latency
        - retrieved chunks
        - final answer
        """

        # 🔍 Measure retrieval latency
        retrieval_stats = measure_latency(
            self.retriever.retrieve,
            query,
            top_k=top_k
        )

        retrieved_chunks = retrieval_stats["result"]
        latency_ms = retrieval_stats["latency_ms"]

        contexts: List[str] = [
            chunk["metadata"]["text"]
            for chunk in retrieved_chunks
            if "text" in chunk["metadata"]
        ]

        if not contexts:
            answer = "I don't know based on the provided context."
        else:
            answer = self.llm.generate(query=query, contexts=contexts)

        return {
            "query": query,
            "answer": answer,
            "retrieval_latency_ms": latency_ms,
            "num_retrieved_chunks": len(retrieved_chunks),
            "retrieved_chunks": retrieved_chunks
        }

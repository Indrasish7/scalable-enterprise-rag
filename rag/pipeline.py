from typing import List
from retrieval.retriever import Retriever
from llm.gemini_llm import GeminiLLM


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.
    """

    def __init__(self, retriever: Retriever, llm: GeminiLLM):
        self.retriever = retriever
        self.llm = llm

    def answer(self, query: str, top_k: int = 5) -> str:
        """
        Generate a grounded answer for a user query.
        """

        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)

        contexts: List[str] = [
            item["metadata"]["text"]
            for item in retrieved_chunks
        ]

        # ✅ Improvement 1: Guard against empty retrieval
        if not contexts:
            return "I don't know based on the provided context."

        # ✅ Improvement 2: Explicitly cap context size
        contexts = contexts[:top_k]

        return self.llm.generate(query=query, contexts=contexts)

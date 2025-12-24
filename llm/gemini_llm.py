import os
from typing import List
from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiLLM:
    """
    Gemini-based LLM wrapper for grounded answer generation.
    """

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY not found in environment")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, query: str, contexts: List[str]) -> str:
        context_block = "\n\n".join(
            f"[Context {i+1}]\n{ctx}" for i, ctx in enumerate(contexts)
        )

        prompt = f"""
You are an AI assistant answering questions strictly using the provided context.

Do NOT use external knowledge.
If the answer is not present, say "I don't know based on the provided context."

Context:
{context_block}

Question:
{query}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        return response.text.strip()

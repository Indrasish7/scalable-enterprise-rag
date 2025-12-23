import re
from typing import List, Dict


class TextCleaner:
    """
    Cleans and normalizes raw document text before chunking and embedding.
    """

    @staticmethod
    def clean(text: str) -> str:
        """
        Apply basic normalization to raw text.

        Steps:
        - Normalize whitespace
        - Remove non-printable characters
        """

        # Normalize whitespace (tabs, newlines → single space)
        text = re.sub(r"\s+", " ", text)

        # Remove non-printable / control characters
        text = re.sub(r"[^\x20-\x7E]", "", text)

        return text.strip()

    def clean_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Clean a list of document dictionaries while preserving metadata.
        """

        cleaned_documents = []

        for doc in documents:
            cleaned_text = self.clean(doc["text"])

            if not cleaned_text:
                continue

            cleaned_documents.append({
                **doc,
                "text": cleaned_text
            })

        return cleaned_documents

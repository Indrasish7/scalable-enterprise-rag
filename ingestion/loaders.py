from typing import Dict

from ingestion.base import BaseLoader
from ingestion.pdf_loader import PDFLoader
from ingestion.docx_loader import DocxLoader


class TextFileLoader(BaseLoader):
    """Loads plain text files."""

    def load(self, source: str):
        import os
        import uuid

        if not os.path.exists(source):
            raise FileNotFoundError(f"Source not found: {source}")

        with open(source, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if not text.strip():
            return []

        return [{
            "id": str(uuid.uuid4()),
            "text": text,
            "metadata": {
                "source": source,
                "type": "txt",
                "size": len(text)
            }
        }]


def get_loader(file_extension: str) -> BaseLoader:
    ext = file_extension.lower().lstrip(".")

    if ext == "txt":
        return TextFileLoader()
    elif ext == "pdf":
        return PDFLoader()
    elif ext == "docx":
        return DocxLoader()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

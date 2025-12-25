import uuid
from typing import List, Dict
from pathlib import Path

from docx import Document
from ingestion.base import BaseLoader


class DocxLoader(BaseLoader):
    """Loads text from DOCX files."""

    def load(self, source: str) -> List[Dict]:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"DOCX not found: {source}")

        document = Document(str(path))
        paragraphs = [
            para.text for para in document.paragraphs if para.text.strip()
        ]

        full_text = "\n".join(paragraphs)

        if not full_text.strip():
            return []

        return [{
            "id": str(uuid.uuid4()),
            "text": full_text,
            "metadata": {
                "source": path.name,
                "type": "docx",
                "paragraphs": len(paragraphs)
            }
        }]

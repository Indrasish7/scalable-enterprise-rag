import uuid
from typing import List, Dict
from pathlib import Path

from pypdf import PdfReader
from ingestion.base import BaseLoader


class PDFLoader(BaseLoader):
    """Loads text from PDF files."""

    def load(self, source: str) -> List[Dict]:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {source}")

        reader = PdfReader(str(path))
        pages_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        full_text = "\n".join(pages_text)

        if not full_text.strip():
            return []

        return [{
            "id": str(uuid.uuid4()),
            "text": full_text,
            "metadata": {
                "source": path.name,
                "type": "pdf",
                "pages": len(reader.pages)
            }
        }]

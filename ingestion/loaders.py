from abc import ABC, abstractmethod
from typing import List, Dict
import os
import uuid


class BaseLoader(ABC):
    """Abstract base class for all document loaders."""

    @abstractmethod
    def load(self, source: str) -> List[Dict]:
        pass


class TextFileLoader(BaseLoader):
    """Loads plain text files."""

    def load(self, source: str) -> List[Dict]:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source not found: {source}")

        documents = []

        if os.path.isdir(source):
            files = [
                os.path.join(source, f)
                for f in sorted(os.listdir(source))
                if f.endswith(".txt")
            ]
        else:
            files = [source]

        for file_path in files:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            if not text.strip():
                continue

            documents.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "metadata": {
                    "source": file_path,
                    "type": "txt",
                    "size": len(text)
                }
            })

        return documents


def get_loader(file_type: str) -> BaseLoader:
    if file_type == "txt":
        return TextFileLoader()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")



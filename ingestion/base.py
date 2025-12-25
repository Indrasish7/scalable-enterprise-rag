from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLoader(ABC):
    """Abstract base class for all document loaders."""

    @abstractmethod
    def load(self, source: str) -> List[Dict]:
        pass

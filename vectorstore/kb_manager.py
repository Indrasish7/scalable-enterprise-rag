import hashlib
import json
import os


class KnowledgeBaseManager:
    def __init__(self, state_path="data/kb_state.json"):
        self.state_path = state_path
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                return json.load(f)
        return {}

    def _save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=2)

    def hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def is_new_or_updated(self, doc_id: str, text: str) -> bool:
        new_hash = self.hash_text(text)
        old_hash = self.state.get(doc_id)
        return new_hash != old_hash

    def update_doc(self, doc_id: str, text: str):
        self.state[doc_id] = self.hash_text(text)
        self._save_state()

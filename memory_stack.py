import json
import os
from typing import List, Dict, Any, Optional

class ShortTermMemory:
    """Sliding window of recent messages."""
    def __init__(self, size: int = 5):
        self.size = size
        self.buffer = []

    def add(self, message: Dict[str, str]):
        self.buffer.append(message)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)

    def get(self) -> List[Dict[str, str]]:
        return self.buffer

class ProfileMemory:
    """KV store for user attributes. Handles conflict by overwriting."""
    def __init__(self, filepath: str = "profile.json"):
        self.filepath = filepath
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                return json.load(f)
        return {}

    def update(self, key: str, value: Any):
        self.data[key] = value
        self._save()

    def get_all(self) -> Dict[str, Any]:
        return self.data

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

class EpisodicMemory:
    """Stores significant past episodes or task outcomes."""
    def __init__(self, filepath: str = "episodes.json"):
        self.filepath = filepath
        self.episodes = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                return json.load(f)
        return []

    def add(self, episode: Dict[str, Any]):
        self.episodes.append(episode)
        self._save()

    def get_recent(self, k: int = 3) -> List[Dict[str, Any]]:
        return self.episodes[-k:]

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.episodes, f, indent=2)

class SemanticMemory:
    """Simple keyword-based search for FAQ/Knowledge (simulation for now)."""
    def __init__(self, data: List[Dict[str, str]]):
        self.knowledge = data

    def search(self, query: str) -> List[str]:
        # Simple keyword matching simulation
        results = []
        query_lower = query.lower()
        for item in self.knowledge:
            if any(keyword in query_lower for keyword in item.get("keywords", [])):
                results.append(item["content"])
        return results[:2]

class MultiMemoryStack:
    def __init__(self):
        self.short_term = ShortTermMemory(size=10)
        self.profile = ProfileMemory()
        self.episodic = EpisodicMemory()
        # Sample knowledge base for semantic memory
        kb = [
            {"keywords": ["policy", "refund"], "content": "Refunds are processed within 5-7 business days."},
            {"keywords": ["shipping", "delivery"], "content": "Standard shipping takes 3-5 days; express is overnight."},
            {"keywords": ["debug", "docker"], "content": "To debug docker services, use 'docker logs <container_id>' or 'docker-compose logs'."}
        ]
        self.semantic = SemanticMemory(kb)

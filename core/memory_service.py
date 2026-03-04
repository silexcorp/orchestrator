"""
memory_service.py — Simple working memory extraction and retrieval.
Mirrors MemoryService.swift (simplified BM25 version, no VecturaKit).
"""
from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from typing import Optional

from models.memory import MemoryEntry, UserProfile


def _config_dir() -> Path:
    p = Path.home() / ".config" / "orchestrator"
    p.mkdir(parents=True, exist_ok=True)
    return p


class MemoryService:
    def __init__(self, path: Optional[Path] = None):
        self._dir = path or _config_dir()
        self._me_path = self._dir / "memory_entries.json"
        self._up_path = self._dir / "user_profiles.json"
        self._lock = threading.Lock()
        self._entries: list[MemoryEntry] = []
        self._profiles: dict[str, UserProfile] = {}
        self._load()

    def _load(self) -> None:
        if self._me_path.exists():
            try:
                self._entries = [
                    MemoryEntry.from_dict(d)
                    for d in json.loads(self._me_path.read_text())
                ]
            except Exception:
                pass
        if self._up_path.exists():
            try:
                for d in json.loads(self._up_path.read_text()):
                    p = UserProfile(**{k: v for k, v in d.items()})
                    self._profiles[p.agent_id] = p
            except Exception:
                pass

    def _save_entries(self) -> None:
        try:
            self._me_path.write_text(json.dumps([e.to_dict() for e in self._entries], indent=2))
        except Exception:
            pass

    def _save_profiles(self) -> None:
        try:
            self._up_path.write_text(json.dumps([p.to_dict() for p in self._profiles.values()], indent=2))
        except Exception:
            pass

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def add_entry(self, entry: MemoryEntry) -> None:
        with self._lock:
            self._entries.append(entry)
            self._save_entries()

    def entries_for_agent(self, agent_id: str) -> list[MemoryEntry]:
        with self._lock:
            return [e for e in self._entries if e.agent_id == agent_id]

    def delete_entry(self, entry_id: str) -> bool:
        with self._lock:
            before = len(self._entries)
            self._entries = [e for e in self._entries if e.id != entry_id]
            if len(self._entries) < before:
                self._save_entries()
                return True
            return False

    def profile_for_agent(self, agent_id: str) -> Optional[UserProfile]:
        with self._lock:
            return self._profiles.get(agent_id)

    def save_profile(self, profile: UserProfile) -> None:
        with self._lock:
            self._profiles[profile.agent_id] = profile
            self._save_profiles()

    # ── Search (simple BM25-style keyword) ────────────────────────────────────

    def search(self, query: str, agent_id: str, limit: int = 10) -> list[MemoryEntry]:
        tokens = set(re.findall(r"\w+", query.lower()))
        with self._lock:
            scored = []
            for e in self._entries:
                if e.agent_id != agent_id:
                    continue
                entry_tokens = set(re.findall(r"\w+", e.content.lower()))
                score = len(tokens & entry_tokens) * e.importance
                if score > 0:
                    scored.append((score, e))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [e for _, e in scored[:limit]]

    def build_context_string(self, query: str, agent_id: str, max_chars: int = 2000) -> str:
        entries = self.search(query, agent_id)
        profile = self.profile_for_agent(agent_id)
        parts = []
        if profile and profile.summary:
            parts.append(f"User Profile:\n{profile.summary}")
        if entries:
            parts.append("Working Memory:")
            for e in entries:
                parts.append(f"- [{e.memory_type}] {e.content}")
        context = "\n".join(parts)
        return context[:max_chars]


# Shared singleton
memory_service = MemoryService()

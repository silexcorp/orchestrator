"""
agent_store.py — Persistent CRUD for Agents and RemoteProviders.
Data is stored in ~/.config/orchestrator/ as JSON files.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from models.agent import Agent, DEFAULT_AGENT
from models.provider import RemoteProvider

if TYPE_CHECKING:
    from models.chat_session import ChatSession


def _config_dir() -> Path:
    p = Path.home() / ".config" / "orchestrator"
    p.mkdir(parents=True, exist_ok=True)
    return p


class AgentStore:
    """Thread-safe, file-backed store for Agents."""

    def __init__(self, path: Optional[Path] = None):
        self._path = path or (_config_dir() / "agents.json")
        self._lock = threading.Lock()
        self._agents: dict[str, Agent] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                for d in data:
                    a = Agent.from_dict(d)
                    self._agents[a.id] = a
            except Exception:
                pass
        # Always ensure the built-in default exists
        if DEFAULT_AGENT.id not in self._agents:
            self._agents[DEFAULT_AGENT.id] = DEFAULT_AGENT

    def _save(self) -> None:
        data = [a.to_dict() for a in self._agents.values()]
        self._path.write_text(json.dumps(data, indent=2))

    def all(self) -> list[Agent]:
        with self._lock:
            return list(self._agents.values())

    def get(self, agent_id: str) -> Optional[Agent]:
        with self._lock:
            return self._agents.get(agent_id)

    def get_default(self) -> Agent:
        with self._lock:
            for a in self._agents.values():
                if a.is_default:
                    return a
            return DEFAULT_AGENT

    def save(self, agent: Agent) -> None:
        with self._lock:
            self._agents[agent.id] = agent
            self._save()

    def delete(self, agent_id: str) -> bool:
        with self._lock:
            if agent_id == DEFAULT_AGENT.id:
                return False  # Cannot delete the built-in default
            removed = self._agents.pop(agent_id, None)
            if removed:
                self._save()
            return removed is not None


class ProviderStore:
    """Thread-safe, file-backed store for RemoteProviders."""

    def __init__(self, path: Optional[Path] = None):
        self._path = path or (_config_dir() / "providers.json")
        self._lock = threading.Lock()
        self._providers: dict[str, RemoteProvider] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                for d in data:
                    p = RemoteProvider.from_dict(d)
                    self._providers[p.id] = p
            except Exception:
                pass

    def _save(self) -> None:
        data = [p.to_dict() for p in self._providers.values()]
        self._path.write_text(json.dumps(data, indent=2))

    def all(self) -> list[RemoteProvider]:
        with self._lock:
            return list(self._providers.values())

    def enabled(self) -> list[RemoteProvider]:
        with self._lock:
            return [p for p in self._providers.values() if p.enabled]

    def get(self, provider_id: str) -> Optional[RemoteProvider]:
        with self._lock:
            return self._providers.get(provider_id)

    def save(self, provider: RemoteProvider) -> None:
        with self._lock:
            self._providers[provider.id] = provider
            self._save()

    def delete(self, provider_id: str) -> bool:
        with self._lock:
            removed = self._providers.pop(provider_id, None)
            if removed:
                self._save()
            return removed is not None


class SessionStore:
    """Thread-safe, file-backed store for ChatSessions."""

    def __init__(self, path: Optional[Path] = None):
        self._path = path or (_config_dir() / "sessions.json")
        self._lock = threading.Lock()
        self._sessions: dict[str, ChatSession] = {}
        self._load()

    def _load(self) -> None:
        from models.chat_session import ChatSession
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                for d in data:
                    s = ChatSession.from_dict(d)
                    self._sessions[s.id] = s
            except Exception:
                pass

    def _save(self) -> None:
        data = [s.to_dict() for s in self._sessions.values()]
        self._path.write_text(json.dumps(data, indent=2))

    def all(self) -> list[ChatSession]:
        with self._lock:
            # Sort by updated_at descending
            return sorted(
                self._sessions.values(),
                key=lambda s: s.updated_at,
                reverse=True,
            )

    def get(self, session_id: str) -> Optional[ChatSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def save(self, session: ChatSession) -> None:
        with self._lock:
            self._sessions[session.id] = session
            self._save()

    def delete(self, session_id: str) -> bool:
        with self._lock:
            removed = self._sessions.pop(session_id, None)
            if removed:
                self._save()
            return removed is not None


# ── Shared singletons ─────────────────────────────────────────────────────────
agent_store = AgentStore()
provider_store = ProviderStore()
session_store = SessionStore()

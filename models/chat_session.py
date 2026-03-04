"""ChatSession and ChatTurn models."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ChatTurn:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"           # "user" | "assistant" | "system" | "tool"
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model: Optional[str] = None
    error: Optional[str] = None
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None

    def to_api_message(self) -> dict:
        """Convert to OpenAI/Ollama message format."""
        msg: dict = {"role": self.role, "content": self.content}
        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        return msg

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "model": self.model,
            "error": self.error,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChatTurn":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ChatSession:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    agent_id: str = "default"
    model: Optional[str] = None
    turns: list[ChatTurn] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    system_prompt: Optional[str] = None  # override agent system prompt

    def add_turn(self, role: str, content: str, model: Optional[str] = None) -> ChatTurn:
        turn = ChatTurn(role=role, content=content, model=model)
        self.turns.append(turn)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        # Auto-title from first user message
        if len(self.turns) == 1 and role == "user":
            words = content.split()
            self.title = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
        return turn

    def to_api_messages(self, system_prompt: Optional[str] = None) -> list[dict]:
        msgs = []
        prompt = system_prompt or self.system_prompt or ""
        if prompt.strip():
            msgs.append({"role": "system", "content": prompt.strip()})
        msgs.extend(t.to_api_message() for t in self.turns)
        return msgs

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "agent_id": self.agent_id,
            "model": self.model,
            "turns": [t.to_dict() for t in self.turns],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "system_prompt": self.system_prompt,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChatSession":
        turns = [ChatTurn.from_dict(t) for t in d.get("turns", [])]
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            title=d.get("title", "New Chat"),
            agent_id=d.get("agent_id", "default"),
            model=d.get("model"),
            turns=turns,
            created_at=d.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=d.get("updated_at", datetime.now(timezone.utc).isoformat()),
            system_prompt=d.get("system_prompt"),
        )

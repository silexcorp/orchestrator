"""Memory models — working memory, user profile, knowledge graph entries."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

MEMORY_TYPES = [
    "fact", "preference", "decision", "correction",
    "commitment", "relationship", "skill", "context",
]


@dataclass
class MemoryEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = "default"
    memory_type: str = "fact"
    content: str = ""
    source_session_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    importance: float = 0.5      # 0.0 – 1.0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "memory_type": self.memory_type,
            "content": self.content,
            "source_session_id": self.source_session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "importance": self.importance,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MemoryEntry":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class UserProfile:
    agent_id: str = "default"
    summary: str = ""
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    explicit_facts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "summary": self.summary,
            "updated_at": self.updated_at,
            "explicit_facts": self.explicit_facts,
        }


@dataclass
class KnowledgeEdge:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = "default"
    subject: str = ""
    relation: str = ""
    obj: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "subject": self.subject,
            "relation": self.relation,
            "obj": self.obj,
            "created_at": self.created_at,
        }

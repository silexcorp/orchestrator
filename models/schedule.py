"""Schedule and Watcher models."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Schedule:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Schedule"
    agent_id: str = "default"
    prompt: str = ""
    frequency: str = "daily"     # "once" | "daily" | "weekly" | "monthly" | "yearly"
    enabled: bool = True
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    last_session_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, d: dict) -> "Schedule":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Watcher:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Watcher"
    folder_path: str = ""
    agent_id: str = "default"
    prompt: str = ""
    enabled: bool = True
    recursive: bool = False
    debounce_ms: int = 1000     # 200 | 1000 | 3000
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, d: dict) -> "Watcher":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Skill:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Skill"
    description: str = ""
    content: str = ""         # Markdown skill content
    source: str = "local"    # "local" | "github"
    source_url: Optional[str] = None
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, d: dict) -> "Skill":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

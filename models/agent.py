"""Agent model — custom AI assistants with unique prompts, tools, and themes."""
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Agent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Agent"
    system_prompt: str = ""
    model: Optional[str] = None          # None = use global default
    temperature: Optional[float] = None  # None = use global default
    max_tokens: Optional[int] = None
    avatar_emoji: str = "🦕"
    theme_color: str = "#7c3aed"
    enabled_tools: list[str] = field(default_factory=list)
    description: str = ""
    is_default: bool = False

    # ── Serialization ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Agent":
        return cls.from_dict(json.loads(text))


# ── Built-in default agent ────────────────────────────────────────────────────

DEFAULT_AGENT = Agent(
    id="default",
    name="Orchestrator",
    system_prompt="",
    avatar_emoji="🦕",
    theme_color="#7c3aed",
    is_default=True,
    description="The default Orchestrator assistant.",
)

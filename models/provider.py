"""Remote provider configuration models."""
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional


PROVIDER_PRESETS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "header_template": {"Authorization": "Bearer {api_key}"},
    },
    "anthropic": {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-sonnet-20241022",
        "header_template": {"x-api-key": "{api_key}", "anthropic-version": "2023-06-01"},
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "anthropic/claude-3.5-sonnet",
        "header_template": {"Authorization": "Bearer {api_key}"},
    },
    "xai": {
        "name": "xAI",
        "base_url": "https://api.x.ai/v1",
        "default_model": "grok-2-latest",
        "header_template": {"Authorization": "Bearer {api_key}"},
    },
    "ollama": {
        "name": "Ollama (Remote)",
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama3.2",
        "header_template": {},
    },
    "custom": {
        "name": "Custom",
        "base_url": "",
        "default_model": "",
        "header_template": {"Authorization": "Bearer {api_key}"},
    },
}


@dataclass
class RemoteProvider:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preset: str = "custom"       # Key in PROVIDER_PRESETS
    name: str = "Custom"
    base_url: str = ""
    api_key: str = ""          # Stored in plain text (keychain would be macOS-only)
    default_model: str = ""
    enabled: bool = True
    custom_headers: dict = field(default_factory=dict)
    timeout: int = 60

    def get_headers(self) -> dict:
        preset_info = PROVIDER_PRESETS.get(self.preset, {})
        template = preset_info.get("header_template", {})
        headers = {"Content-Type": "application/json"}
        for k, v in template.items():
            headers[k] = v.replace("{api_key}", self.api_key)
        headers.update(self.custom_headers)
        return headers

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RemoteProvider":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

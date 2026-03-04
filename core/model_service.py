"""
model_service.py — Routing and streaming for Ollama (local) and Remote Providers.

Mirrors:
  - MLXService (-> OllamaService)
  - RemoteProviderService
  - ModelServiceRouter
"""
from __future__ import annotations

import json
import threading
from typing import Iterator, Optional, Callable
import httpx

OLLAMA_BASE = "http://localhost:11434"


# ══════════════════════════════════════════════════════════════════════════════
# Ollama Service  (replaces MLXService + ModelRuntime)
# ══════════════════════════════════════════════════════════════════════════════

class OllamaService:
    """Thin wrapper around the Ollama REST API for local model inference."""

    def __init__(self, base_url: str = OLLAMA_BASE):
        self.base_url = base_url.rstrip("/")

    # ── Model management ─────────────────────────────────────────────────────

    def list_models(self) -> list[dict]:
        """Return list of locally available models."""
        try:
            r = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            return r.json().get("models", [])
        except Exception:
            return []

    def model_names(self) -> list[str]:
        return [m["name"] for m in self.list_models()]

    def pull_model(
        self,
        name: str,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> Iterator[dict]:
        """Stream pull progress events. Yields dicts with 'status' and optional 'completed'/'total'."""
        with httpx.stream(
            "POST",
            f"{self.base_url}/api/pull",
            json={"name": name, "stream": True},
            timeout=3600,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    event = json.loads(line)
                    if progress_cb:
                        progress_cb(event)
                    yield event

    def delete_model(self, name: str) -> bool:
        try:
            r = httpx.post(f"{self.base_url}/api/delete", json={"name": name}, timeout=10)
            return r.status_code in (200, 204)
        except Exception:
            return False

    def is_running(self) -> bool:
        try:
            httpx.get(f"{self.base_url}/api/tags", timeout=2)
            return True
        except Exception:
            return False

    # ── Inference ─────────────────────────────────────────────────────────────

    def stream_chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 16384,
        stop: Optional[list[str]] = None,
    ) -> Iterator[str]:
        """Yield text tokens one by one via Ollama /api/chat stream."""
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if stop:
            payload["options"]["stop"] = stop

        with httpx.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    if content := data.get("message", {}).get("content"):
                        yield content
                    if data.get("done"):
                        break

    def has_model(self, name: str) -> bool:
        return name in self.model_names()


# ══════════════════════════════════════════════════════════════════════════════
# Remote Provider Service  (wraps OpenAI-compatible + Anthropic endpoints)
# ══════════════════════════════════════════════════════════════════════════════

class RemoteProviderService:
    """Streams chat completions from a remote OpenAI-compatible provider."""

    def __init__(self, base_url: str, headers: dict, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.timeout = timeout

    def stream_chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stop: Optional[list[str]] = None,
    ) -> Iterator[str]:
        """Yield text deltas via SSE /v1/chat/completions stream."""
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if stop:
            payload["stop"] = stop

        with httpx.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        delta = (
                            data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, IndexError):
                        continue

    def list_models(self) -> list[str]:
        try:
            r = httpx.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10,
            )
            r.raise_for_status()
            return [m["id"] for m in r.json().get("data", [])]
        except Exception:
            return []


# ══════════════════════════════════════════════════════════════════════════════
# Anthropic-specific service (different auth + API shape)
# ══════════════════════════════════════════════════════════════════════════════

class AnthropicService:
    """Streams from Anthropic /v1/messages endpoint."""

    def __init__(self, api_key: str, timeout: int = 60):
        self.base_url = "https://api.anthropic.com"
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def stream_chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        stop: Optional[list[str]] = None,
    ) -> Iterator[str]:
        user_msgs = [m for m in messages if m["role"] != "system"]
        sys_prompt = system or next(
            (m["content"] for m in messages if m["role"] == "system"), None
        )
        payload: dict = {
            "model": model,
            "messages": user_msgs,
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if sys_prompt:
            payload["system"] = sys_prompt
        if stop:
            payload["stop_sequences"] = stop

        with httpx.stream(
            "POST",
            f"{self.base_url}/v1/messages",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or line.startswith("event:"):
                    continue
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {}).get("text", "")
                            if delta:
                                yield delta
                    except json.JSONDecodeError:
                        continue


# ══════════════════════════════════════════════════════════════════════════════
# Router  (picks the right service for a given model name)
# ══════════════════════════════════════════════════════════════════════════════

class ModelServiceRouter:
    """
    Maintains a registry of services and routes chat requests to the
    appropriate one based on the model name.
    """

    def __init__(self):
        self.ollama = OllamaService()
        self._remote_services: dict[str, tuple[RemoteProviderService, str]] = {}
        # model_name -> (service, canonical_model_name)
        self._anthropic_services: dict[str, tuple[AnthropicService, str]] = {}
        self._lock = threading.Lock()

    def register_remote_provider(
        self,
        provider_id: str,
        service: RemoteProviderService,
        model_names: list[str],
    ) -> None:
        with self._lock:
            for name in model_names:
                self._remote_services[name] = (service, name)

    def register_anthropic(
        self,
        provider_id: str,
        service: AnthropicService,
        model_names: list[str],
    ) -> None:
        with self._lock:
            for name in model_names:
                self._anthropic_services[name] = (service, name)

    def clear_provider(self, provider_id: str) -> None:
        pass  # Simplified; full impl tracks per-provider

    def resolve_stream(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stop: Optional[list[str]] = None,
    ) -> Iterator[str]:
        """Resolve and stream from the correct backend."""
        with self._lock:
            if model in self._anthropic_services:
                svc, canonical = self._anthropic_services[model]
                sys_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
                user_msgs = [m for m in messages if m["role"] != "system"]
                return svc.stream_chat(canonical, user_msgs, temperature, max_tokens, sys_msg, stop)
            if model in self._remote_services:
                svc, canonical = self._remote_services[model]
                return svc.stream_chat(canonical, messages, temperature, max_tokens, stop)

        # Fall back to Ollama local
        return self.ollama.stream_chat(model, messages, temperature, max_tokens, stop)

    def all_model_names(self) -> list[str]:
        """All models: local Ollama + all registered remotes."""
        names: list[str] = self.ollama.model_names()
        with self._lock:
            names += list(self._remote_services.keys())
            names += list(self._anthropic_services.keys())
        seen: set[str] = set()
        result = []
        for n in names:
            if n not in seen:
                seen.add(n)
                result.append(n)
        return result


# ── Shared global router instance ─────────────────────────────────────────────
router = ModelServiceRouter()

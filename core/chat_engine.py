"""
chat_engine.py — Orchestrates chat streaming through model_service.
Mirrors ChatEngine.swift.
"""
from __future__ import annotations

import threading
from typing import Iterator, Optional, Callable

from core.model_service import router as _default_router, ModelServiceRouter
from models.agent import Agent, DEFAULT_AGENT


class ChatEngine:
    """
    Routes chat requests to the correct ModelService and streams tokens.
    Thread-safe; streaming runs on a background thread and calls `on_token`
    on each text delta, then `on_done` or `on_error` when finished.
    """

    def __init__(self, service_router: Optional[ModelServiceRouter] = None):
        self._router = service_router or _default_router

    # ── Public API ────────────────────────────────────────────────────────────

    def stream_chat(
        self,
        messages: list[dict],
        model: str,
        agent: Optional[Agent] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        on_token: Optional[Callable[[str], None]] = None,
        on_done: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """
        Start streaming in a background thread.
        Returns the thread (already started).
        """
        eff_agent = agent or DEFAULT_AGENT
        eff_temp = temperature if temperature is not None else 0.7
        eff_max = max_tokens if max_tokens is not None else 4096
        eff_model = model

        enriched = self._enrich_with_system_prompt(messages, eff_agent)

        def _run():
            try:
                for token in self._router.resolve_stream(
                    model=eff_model,
                    messages=enriched,
                    temperature=eff_temp,
                    max_tokens=eff_max,
                ):
                    if on_token:
                        on_token(token)
                if on_done:
                    on_done()
            except Exception as exc:
                if on_error:
                    on_error(str(exc))

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return t

    def stop_stream(self, thread: Optional[threading.Thread]) -> None:
        """
        Streaming cannot be forcefully stopped from outside in this sync model.
        The calling UI should set a flag that the thread checks periodically.
        This method exists for API symmetry with Swift's ChatEngine.
        """
        pass  # Thread is daemon; UI sets _stop flag in StreamWorker

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _enrich_with_system_prompt(
        messages: list[dict],
        agent: Agent,
    ) -> list[dict]:
        """Prepend system prompt if not already present."""
        has_system = any(m.get("role") == "system" for m in messages)
        if has_system or not agent.system_prompt.strip():
            return messages
        return [{"role": "system", "content": agent.system_prompt.strip()}] + messages

    @staticmethod
    def estimate_tokens(messages: list[dict]) -> int:
        total_chars = sum(len(m.get("content") or "") for m in messages)
        return max(1, total_chars // 4)

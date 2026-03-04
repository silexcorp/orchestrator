"""
insights_service.py — Request/inference logging (mirrors InsightsService.swift).
Stores logs in memory (last 500) and persists to ~/.config/orchestrator/insights.json.
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def _config_dir() -> Path:
    p = Path.home() / ".config" / "orchestrator"
    p.mkdir(parents=True, exist_ok=True)
    return p


@dataclass
class InferenceLog:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = "chat_ui"        # "chat_ui" | "http_api"
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    finish_reason: str = "stop"    # "stop" | "error" | "cancelled"
    error_message: Optional[str] = None
    tokens_per_second: float = 0.0

    def __post_init__(self):
        if self.duration_ms > 0 and self.output_tokens > 0:
            self.tokens_per_second = self.output_tokens / (self.duration_ms / 1000)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "InferenceLog":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class InsightsService:
    MAX_LOGS = 500

    def __init__(self, path: Optional[Path] = None):
        self._path = path or (_config_dir() / "insights.json")
        self._lock = threading.Lock()
        self._logs: list[InferenceLog] = []
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                self._logs = [InferenceLog.from_dict(d) for d in data[-self.MAX_LOGS:]]
            except Exception:
                pass

    def _save(self) -> None:
        try:
            data = [l.to_dict() for l in self._logs[-self.MAX_LOGS:]]
            self._path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def log(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: float,
        source: str = "chat_ui",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        finish_reason: str = "stop",
        error_message: Optional[str] = None,
    ) -> InferenceLog:
        log = InferenceLog(
            source=source,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            temperature=temperature,
            max_tokens=max_tokens,
            finish_reason=finish_reason,
            error_message=error_message,
        )
        with self._lock:
            self._logs.append(log)
            if len(self._logs) > self.MAX_LOGS:
                self._logs = self._logs[-self.MAX_LOGS:]
            self._save()
        return log

    def all(self) -> list[InferenceLog]:
        with self._lock:
            return list(reversed(self._logs))

    def clear(self) -> None:
        with self._lock:
            self._logs.clear()
            self._save()

    def stats(self) -> dict:
        with self._lock:
            if not self._logs:
                return {"total": 0, "success_rate": 1.0, "avg_latency_ms": 0.0, "avg_tps": 0.0}
            total = len(self._logs)
            errors = sum(1 for l in self._logs if l.finish_reason == "error")
            avg_lat = sum(l.duration_ms for l in self._logs) / total
            tps_list = [l.tokens_per_second for l in self._logs if l.tokens_per_second > 0]
            avg_tps = sum(tps_list) / len(tps_list) if tps_list else 0.0
            return {
                "total": total,
                "success_rate": (total - errors) / total,
                "avg_latency_ms": avg_lat,
                "avg_tps": avg_tps,
            }


# Shared singleton
insights = InsightsService()

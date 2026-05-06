from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _float_env(name: str, default: float) -> float:
    raw_value = os.environ.get(name)
    if raw_value is None or raw_value == "":
        return default
    return float(raw_value)


def _int_env(name: str, default: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None or raw_value == "":
        return default
    return int(raw_value)


@dataclass(frozen=True)
class MessagePolishingSettings:
    api_key: Optional[str]
    base_url: str = "https://api.upstage.ai/v1"
    model: str = "solar-pro3"
    temperature: float = 0.2
    timeout_seconds: float = 60.0
    poll_interval_seconds: float = 2.0
    max_poll_seconds: float = 120.0
    max_feedback_iterations: int = 2

    @classmethod
    def from_env(cls) -> "MessagePolishingSettings":
        return cls(
            api_key=os.environ.get("UPSTAGE_API_KEY"),
            base_url=os.environ.get("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1"),
            model=os.environ.get("UPSTAGE_MODEL", "solar-pro3"),
            temperature=_float_env("UPSTAGE_TEMPERATURE", 0.2),
            timeout_seconds=_float_env("UPSTAGE_TIMEOUT_SECONDS", 60.0),
            poll_interval_seconds=_float_env("UPSTAGE_POLL_INTERVAL_SECONDS", 2.0),
            max_poll_seconds=_float_env("UPSTAGE_MAX_POLL_SECONDS", 120.0),
            max_feedback_iterations=_int_env("MESSAGE_POLISHING_MAX_FEEDBACK_ITERATIONS", 2),
        )

    def require_api_key(self) -> str:
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY is required to call the Upstage API.")
        return self.api_key

    @property
    def chat_base_url(self) -> str:
        normalized = self.base_url.rstrip("/")
        if normalized.endswith("/v2"):
            return f"{normalized[:-3]}/v1"
        return normalized

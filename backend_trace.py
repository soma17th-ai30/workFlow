from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


TRUTHY_VALUES = {"1", "true", "yes", "on"}


def backend_trace_enabled() -> bool:
    return os.environ.get("MESSAGE_POLISHING_TRACE", "").strip().lower() in TRUTHY_VALUES


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def print_agent_trace(
    *,
    session_id: str | None,
    agent: str,
    direction: str,
    payload: Any,
) -> None:
    if not backend_trace_enabled():
        return

    trace_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "agent": agent,
        "direction": direction,
        "payload": _to_jsonable(payload),
    }
    print(
        "[agent-trace] "
        + json.dumps(trace_payload, ensure_ascii=False, indent=2, default=str),
        flush=True,
    )

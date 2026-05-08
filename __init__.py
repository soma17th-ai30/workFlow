from __future__ import annotations

import sys

sys.modules.setdefault("message_polishing", sys.modules[__name__])

from message_polishing.schemas import MessagePolishingInput, MessagePolishingOutput


def run_message_polishing_workflow(*args, **kwargs):
    from message_polishing.graph import run_message_polishing_workflow as _run_message_polishing_workflow

    return _run_message_polishing_workflow(*args, **kwargs)

__all__ = [
    "MessagePolishingInput",
    "MessagePolishingOutput",
    "run_message_polishing_workflow",
]

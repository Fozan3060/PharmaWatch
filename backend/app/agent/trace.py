"""TraceEvent shapes streamed to the frontend over SSE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Event types the orchestrator emits.
EVENT_TYPES = {
    "started",       # investigation begun, payload: {input}
    "thinking",      # agent text between tool calls, payload: {text}
    "tool_call",     # about to invoke a tool, payload: {name, args}
    "tool_result",   # tool returned, payload: {name, result}
    "tool_error",    # tool raised, payload: {name, error}
    "final",         # final synthesized response, payload: {text}
    "error",         # orchestrator-level failure, payload: {reason, ...}
}


@dataclass(frozen=True)
class TraceEvent:
    type: str
    sequence: int
    timestamp: str
    data: dict[str, Any]

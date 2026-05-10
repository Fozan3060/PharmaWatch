"""The PharmaWatch agent loop.

Plan -> Execute -> Evaluate -> Loop -> Conclude. Yields TraceEvent objects as
the agent works so the frontend can render the agent's reasoning live via SSE.

The chat session is injected, so tests pass in a fake without touching the
real Gemini SDK.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from google.genai import types

from app.agent.gemini_client import make_chat
from app.agent.tools import dispatch
from app.agent.trace import TraceEvent
from app.config import get_settings


def _event(seq: int, type_: str, data: dict[str, Any]) -> TraceEvent:
    return TraceEvent(
        type=type_,
        sequence=seq,
        timestamp=datetime.now(UTC).isoformat(),
        data=data,
    )


def _extract_parts(response: Any) -> tuple[list[Any], list[str]]:
    """Pull function_calls and text fragments out of a Gemini response."""
    parts = response.candidates[0].content.parts
    fcs = [p.function_call for p in parts if getattr(p, "function_call", None) and p.function_call.name]
    texts = [p.text for p in parts if getattr(p, "text", None)]
    return fcs, texts


def _summarize(result: Any, max_list: int = 5) -> Any:
    """Trim large lists in the trace stream so the FE doesn't drown.
    The full untruncated result still goes back to the model."""
    if isinstance(result, dict):
        out: dict[str, Any] = {}
        for k, v in result.items():
            if isinstance(v, list) and len(v) > max_list:
                out[k] = [*v[:max_list], {"_truncated": True, "remaining": len(v) - max_list}]
            else:
                out[k] = v
        return out
    return result


async def investigate(user_input: str, chat: Any | None = None) -> AsyncIterator[TraceEvent]:
    settings = get_settings()
    chat = chat or make_chat()
    seq = 0

    seq += 1
    yield _event(seq, "started", {"input": user_input, "model": settings.gemini_agent_model})

    response = await chat.send_message(user_input)

    for _ in range(settings.agent_max_tool_calls):
        function_calls, texts = _extract_parts(response)

        if texts:
            seq += 1
            yield _event(seq, "thinking", {"text": "\n".join(t for t in texts if t).strip()})

        if not function_calls:
            seq += 1
            final_text = "\n".join(t for t in texts if t).strip()
            yield _event(seq, "final", {"text": final_text})
            return

        function_response_parts: list[types.Part] = []
        for fc in function_calls:
            args = dict(fc.args) if fc.args else {}
            seq += 1
            yield _event(seq, "tool_call", {"name": fc.name, "args": args})
            try:
                result = await dispatch(fc.name, **args)
                seq += 1
                yield _event(seq, "tool_result", {"name": fc.name, "result": _summarize(result)})
                function_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response={"result": result})
                )
            except Exception as exc:
                seq += 1
                yield _event(seq, "tool_error", {"name": fc.name, "error": str(exc)})
                function_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response={"error": str(exc)})
                )

        response = await chat.send_message(function_response_parts)

    seq += 1
    yield _event(
        seq,
        "error",
        {"reason": "max_tool_calls_exceeded", "limit": settings.agent_max_tool_calls},
    )

"""Tool registry for the Gemini agent.

Tools self-register via @tool. Adding a tool = drop a file under
app/agent/tools/<category>/ and decorate the function. The orchestrator
imports `app.agent.tools` and gets every tool.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.core.exceptions import ToolExecutionError, ToolNotFoundError


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]


_REGISTRY: dict[str, ToolSpec] = {}


def tool(*, name: str, description: str, parameters: dict[str, Any]):
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if name in _REGISTRY:
            raise ValueError(f"Duplicate tool name: {name}")
        _REGISTRY[name] = ToolSpec(name=name, description=description,
                                   parameters=parameters, handler=fn)
        return fn

    return decorator


def all_tools() -> list[ToolSpec]:
    return list(_REGISTRY.values())


def get_tool(name: str) -> ToolSpec:
    if name not in _REGISTRY:
        raise ToolNotFoundError(f"Unknown tool: {name}")
    return _REGISTRY[name]


async def dispatch(name: str, **kwargs: Any) -> Any:
    spec = get_tool(name)
    try:
        result = spec.handler(**kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result
    except Exception as exc:
        raise ToolExecutionError(f"Tool '{name}' failed: {exc}") from exc


def to_gemini_function_declarations() -> list[dict[str, Any]]:
    """Format the registry for Gemini's `tools=[Tool(function_declarations=...)]` API."""
    return [
        {"name": s.name, "description": s.description, "parameters": s.parameters}
        for s in all_tools()
    ]

"""Minimal Gemini chat fake for orchestrator tests.

Implements just the slice the orchestrator touches: send_message_async()
returning a response whose .candidates[0].content.parts is a list with
optional .text and .function_call attributes.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FakeFunctionCall:
    name: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class FakePart:
    text: str | None = None
    function_call: FakeFunctionCall | None = None


@dataclass
class _FakeContent:
    parts: list[FakePart]


@dataclass
class _FakeCandidate:
    content: _FakeContent


@dataclass
class FakeResponse:
    parts: list[FakePart]

    @property
    def candidates(self) -> list[_FakeCandidate]:
        return [_FakeCandidate(_FakeContent(self.parts))]


class FakeChat:
    """Yields scripted responses in order. Records every message sent."""

    def __init__(self, scripted: Iterable[FakeResponse]):
        self._iter = iter(scripted)
        self.sent: list[Any] = []

    async def send_message(self, message: Any) -> FakeResponse:
        self.sent.append(message)
        try:
            return next(self._iter)
        except StopIteration as exc:
            raise AssertionError(
                "FakeChat ran out of scripted responses — orchestrator made an unexpected call"
            ) from exc

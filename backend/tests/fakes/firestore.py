"""Minimal in-memory Firestore stand-in for tests.

Implements the small slice of the Firestore Admin SDK that PharmaWatch uses:
collection().add(), collection().where().where().stream(), and stream().
"""

from __future__ import annotations

import operator
import uuid
from collections.abc import Iterator
from typing import Any

_OPS = {
    "==": operator.eq,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}


class _Doc:
    def __init__(self, doc_id: str, data: dict[str, Any]):
        self.id = doc_id
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class _Query:
    def __init__(self, docs: list[_Doc], filters: list[tuple[str, str, Any]]):
        self._docs = docs
        self._filters = filters

    def where(self, field: str, op: str, value: Any) -> _Query:
        return _Query(self._docs, [*self._filters, (field, op, value)])

    def stream(self) -> Iterator[_Doc]:
        for d in self._docs:
            if all(_OPS[op](d._data.get(field), value) for field, op, value in self._filters):
                yield d


class _Collection:
    def __init__(self, docs: list[_Doc]):
        self._docs = docs

    def add(self, data: dict[str, Any]) -> tuple[Any, _Doc]:
        doc = _Doc(uuid.uuid4().hex, dict(data))
        self._docs.append(doc)
        return (None, doc)

    def where(self, field: str, op: str, value: Any) -> _Query:
        return _Query(self._docs, [(field, op, value)])

    def stream(self) -> Iterator[_Doc]:
        return iter(self._docs)


class FakeFirestore:
    def __init__(self) -> None:
        self._collections: dict[str, list[_Doc]] = {}

    def collection(self, name: str) -> _Collection:
        return _Collection(self._collections.setdefault(name, []))

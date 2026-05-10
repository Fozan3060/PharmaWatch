"""Firestore reads/writes for the community_reports collection.

Privacy invariant: NO PII fields. Only pharmacy + medicine + price + a one-way
session hash for rate-limiting.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.data.firebase.client import get_firestore

COLLECTION = "community_reports"


def add_report(record: dict[str, Any]) -> str:
    """Write one report. Returns the new document ID."""
    db = get_firestore()
    payload = {**record, "timestamp": datetime.now(UTC)}
    _, doc_ref = db.collection(COLLECTION).add(payload)
    return doc_ref.id


def reports_for_pharmacy(pharmacy_id: str, days: int = 30) -> list[dict[str, Any]]:
    """Single-field query (auto-indexed); the timestamp window is filtered in
    Python so we don't need a Firestore composite index for (pharmacyId, timestamp).
    Fine at hackathon scale; revisit with a composite index if a single pharmacy
    ever holds tens of thousands of reports."""
    db = get_firestore()
    cutoff = datetime.now(UTC) - timedelta(days=days)
    query = db.collection(COLLECTION).where("pharmacyId", "==", pharmacy_id)
    out: list[dict[str, Any]] = []
    for d in query.stream():
        data = d.to_dict()
        ts = data.get("timestamp")
        if ts is None or ts >= cutoff:
            out.append({"id": d.id, **data})
    return out


def all_recent_reports(days: int = 30) -> list[dict[str, Any]]:
    """All reports in the rolling window, used to render the heatmap."""
    db = get_firestore()
    cutoff = datetime.now(UTC) - timedelta(days=days)
    query = db.collection(COLLECTION).where("timestamp", ">=", cutoff)
    return [{"id": d.id, **d.to_dict()} for d in query.stream()]

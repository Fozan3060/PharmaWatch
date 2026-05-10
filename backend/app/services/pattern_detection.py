"""Pattern detection over the community_reports stream.

Per SRS §3.7 Feature 7 (Crowdsourced Fraud Heatmap):
    1-3 reports   -> watch       (yellow dot)
    4-9 reports   -> suspicious  (orange dot)
    10+ reports   -> confirmed   (red dot, triggers collective dossier)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def classify(report_count: int) -> str:
    if report_count <= 0:
        return "clean"
    if report_count <= 3:
        return "watch"
    if report_count <= 9:
        return "suspicious"
    return "confirmed"


def summarize_pharmacy(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate stats for a single pharmacy from its raw reports."""
    if not reports:
        return {
            "report_count": 0,
            "classification": "clean",
            "medicines_flagged": [],
            "avg_overcharge_pct": 0.0,
            "earliest_report": None,
            "latest_report": None,
        }

    medicines = sorted({r["medicine"] for r in reports if r.get("medicine")})
    pcts = [r["overchargePct"] for r in reports if r.get("overchargePct") is not None]
    timestamps = sorted(r["timestamp"] for r in reports if r.get("timestamp"))

    return {
        "report_count": len(reports),
        "classification": classify(len(reports)),
        "medicines_flagged": medicines,
        "avg_overcharge_pct": round(sum(pcts) / len(pcts), 1) if pcts else 0.0,
        "earliest_report": timestamps[0] if timestamps else None,
        "latest_report": timestamps[-1] if timestamps else None,
    }


def aggregate_for_heatmap(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group all recent reports by pharmacy and classify each."""
    by_pharmacy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in reports:
        pid = r.get("pharmacyId")
        if pid:
            by_pharmacy[pid].append(r)

    out = []
    for pid, group in by_pharmacy.items():
        summary = summarize_pharmacy(group)
        sample = group[0]
        out.append(
            {
                "pharmacy_id": pid,
                "pharmacy_name": sample.get("pharmacyName"),
                "city": sample.get("city"),
                "area": sample.get("area"),
                **summary,
            }
        )
    out.sort(key=lambda p: p["report_count"], reverse=True)
    return out

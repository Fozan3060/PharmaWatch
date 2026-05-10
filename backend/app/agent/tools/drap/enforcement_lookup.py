"""drap_enforcement_lookup — the Investigation Report data source.

Returns the pharmacy's prior DRAP enforcement history (fines, suspensions,
notice references, source URLs). This is the "undeniable evidence" that
distinguishes PharmaWatch from a price checker.
"""

from __future__ import annotations

from app.agent.tools.base import tool
from app.data.drap.repository import find_enforcement_by_pharmacy
from app.normalization.pharmacy_names import make_pharmacy_id


@tool(
    name="drap_enforcement_lookup",
    description=(
        "Retrieve the pharmacy's prior DRAP enforcement history — fines, license suspensions, "
        "counterfeit-sale notices, with official notice references and source URLs. This is the "
        "evidence base for the Investigation Report. Always call this when investigating a "
        "pharmacy complaint, even if the current overcharge is small."
    ),
    parameters={
        "type": "object",
        "properties": {
            "pharmacy_name": {
                "type": "string",
                "description": "Pharmacy name as reported by the user.",
            },
            "city": {
                "type": "string",
                "description": "City of the pharmacy (e.g. 'Karachi', 'Lahore').",
            },
            "area": {
                "type": "string",
                "description": "Neighborhood or area within the city (e.g. 'Saddar', 'DHA Phase 5').",
            },
        },
        "required": ["pharmacy_name", "city"],
    },
)
def drap_enforcement_lookup(
    pharmacy_name: str,
    city: str,
    area: str | None = None,
) -> dict:
    pharmacy_id = make_pharmacy_id(pharmacy_name, area, city)
    rows = find_enforcement_by_pharmacy(pharmacy_id=pharmacy_id)

    if not rows:
        rows = find_enforcement_by_pharmacy(pharmacy_name=pharmacy_name, city=city)

    if not rows:
        return {
            "found": False,
            "pharmacy_id": pharmacy_id,
            "queried": {"pharmacy_name": pharmacy_name, "city": city, "area": area},
        }

    total_fines = sum(r["penalty_amount_pkr"] or 0 for r in rows)
    severity_counts: dict[str, int] = {}
    for r in rows:
        severity_counts[r["severity"]] = severity_counts.get(r["severity"], 0) + 1

    return {
        "found": True,
        "pharmacy_id": pharmacy_id,
        "violation_count": len(rows),
        "summary": {
            "total_fines_pkr": total_fines,
            "severity_breakdown": severity_counts,
            "earliest_violation": rows[-1]["violation_date"],
            "latest_violation": rows[0]["violation_date"],
        },
        "violations": [
            {
                "violation_type": r["violation_type"],
                "violation_date": r["violation_date"],
                "medicine_involved": r["medicine_involved"],
                "description": r["description"],
                "penalty_type": r["penalty_type"],
                "penalty_amount_pkr": r["penalty_amount_pkr"],
                "suspension_days": r["suspension_days"],
                "drap_notice_ref": r["drap_notice_ref"],
                "source_url": r["source_url"],
                "severity": r["severity"],
                "is_resolved": bool(r["is_resolved"]),
            }
            for r in rows
        ],
    }

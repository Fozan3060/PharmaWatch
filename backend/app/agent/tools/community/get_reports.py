from __future__ import annotations

from app.agent.tools.base import tool
from app.data.firebase import reports_repo
from app.normalization.pharmacy_names import make_pharmacy_id
from app.services.pattern_detection import summarize_pharmacy


@tool(
    name="get_pharmacy_reports",
    description=(
        "Aggregate community fraud reports for a single pharmacy over the last 30 days. "
        "Returns count, watch/suspicious/confirmed classification, list of medicines "
        "flagged, and average overcharge percentage. The agent uses the classification "
        "to decide whether to trigger a collective dossier (10+ reports = confirmed)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "pharmacy_name": {"type": "string"},
            "city": {"type": "string"},
            "area": {"type": "string"},
        },
        "required": ["pharmacy_name", "city"],
    },
)
def get_pharmacy_reports(pharmacy_name: str, city: str, area: str | None = None) -> dict:
    pharmacy_id = make_pharmacy_id(pharmacy_name, area, city)
    reports = reports_repo.reports_for_pharmacy(pharmacy_id)
    summary = summarize_pharmacy(reports)
    return {
        "pharmacy_id": pharmacy_id,
        "pharmacy_name": pharmacy_name,
        "city": city,
        "area": area,
        **summary,
        "reports": [
            {
                "medicine": r.get("medicine"),
                "officialMRP": r.get("officialMRP"),
                "chargedPrice": r.get("chargedPrice"),
                "overchargePct": r.get("overchargePct"),
                "timestamp": r.get("timestamp"),
            }
            for r in reports
        ],
    }

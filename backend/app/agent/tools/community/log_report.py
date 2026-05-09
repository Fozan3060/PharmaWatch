from __future__ import annotations

from app.agent.tools.base import tool
from app.data.firebase import reports_repo
from app.normalization.pharmacy_names import make_pharmacy_id
from app.services.pattern_detection import classify


@tool(
    name="log_community_report",
    description=(
        "Anonymously log an overcharge report to the community heatmap. Call this AFTER "
        "drap_price_lookup confirms an overcharge — never log a report whose overcharge "
        "has not been verified against DRAP MRP. Returns the updated 30-day report count "
        "for the pharmacy so the agent can decide whether to escalate to a collective dossier."
    ),
    parameters={
        "type": "object",
        "properties": {
            "pharmacy_name": {"type": "string"},
            "city": {"type": "string"},
            "area": {"type": "string"},
            "medicine": {"type": "string"},
            "official_mrp": {"type": "number", "description": "DRAP-registered MRP in PKR"},
            "charged_price": {"type": "number", "description": "Price the user was actually charged in PKR"},
        },
        "required": ["pharmacy_name", "city", "medicine", "official_mrp", "charged_price"],
    },
)
def log_community_report(
    pharmacy_name: str,
    city: str,
    medicine: str,
    official_mrp: float,
    charged_price: float,
    area: str | None = None,
) -> dict:
    pharmacy_id = make_pharmacy_id(pharmacy_name, area, city)
    overcharge_amt = round(charged_price - official_mrp, 2)
    overcharge_pct = round((overcharge_amt / official_mrp) * 100, 1) if official_mrp else 0.0

    report_id = reports_repo.add_report(
        {
            "pharmacyId": pharmacy_id,
            "pharmacyName": pharmacy_name,
            "area": area,
            "city": city,
            "medicine": medicine,
            "officialMRP": official_mrp,
            "chargedPrice": charged_price,
            "overchargeAmt": overcharge_amt,
            "overchargePct": overcharge_pct,
        }
    )
    pharmacy_reports = reports_repo.reports_for_pharmacy(pharmacy_id)
    count = len(pharmacy_reports)

    return {
        "logged": True,
        "report_id": report_id,
        "pharmacy_id": pharmacy_id,
        "pharmacy_total_reports_30d": count,
        "classification": classify(count),
    }

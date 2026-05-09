"""Compose a collective DRAP dossier for a pharmacy with multiple community reports.

For each report, cross-checks the claimed overcharge against the *current* DRAP
MRP — so the dossier presents only verified incidents. Pulls the pharmacy's
prior enforcement history and combines into a single evidence package.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from app.data.drap.repository import find_enforcement_by_pharmacy, find_medicine_by_brand
from app.data.firebase import reports_repo
from app.normalization.medicine_names import normalize
from app.normalization.pharmacy_names import make_pharmacy_id


def _verify_report(report: dict[str, Any]) -> dict[str, Any]:
    medicine = report.get("medicine", "")
    record = find_medicine_by_brand(normalize(medicine))
    if not record:
        return {**report, "verified": False, "verification_note": "medicine_not_in_drap_db"}

    drap_mrp = record["mrp_pkr"]
    charged = report.get("chargedPrice", 0)
    if charged <= drap_mrp:
        return {**report, "verified": False, "verification_note": "claim_within_mrp"}

    return {
        **report,
        "verified": True,
        "drap_mrp_now": drap_mrp,
        "drap_reg_number": record["reg_number"],
        "verified_overcharge_pct": round((charged - drap_mrp) / drap_mrp * 100, 1),
    }


def compose_dossier(
    *, pharmacy_name: str, pharmacy_city: str, pharmacy_area: str | None = None
) -> dict[str, Any]:
    pharmacy_id = make_pharmacy_id(pharmacy_name, pharmacy_area, pharmacy_city)
    raw_reports = reports_repo.reports_for_pharmacy(pharmacy_id)
    enforcement = find_enforcement_by_pharmacy(pharmacy_id=pharmacy_id)

    verified_reports = [_verify_report(r) for r in raw_reports]
    verified_only = [r for r in verified_reports if r["verified"]]
    medicines = sorted({r["medicine"] for r in verified_only if r.get("medicine")})
    pcts = [r["verified_overcharge_pct"] for r in verified_only]
    avg_overcharge = round(sum(pcts) / len(pcts), 1) if pcts else 0.0

    pharmacy_full = ", ".join(p for p in [pharmacy_area, pharmacy_city] if p)

    summary_section = {
        "heading": "Case Summary",
        "paragraphs": [
            f"Pharmacy: {pharmacy_name}, {pharmacy_full}",
            f"Verified incidents: {len(verified_only)} of {len(raw_reports)} community reports",
            f"Distinct medicines involved: {len(medicines)}",
            f"Average overcharge across verified incidents: {avg_overcharge}%",
            f"Prior DRAP enforcement actions: {len(enforcement)}",
        ],
    }

    incidents_section = {
        "heading": "Verified Incidents",
        "rows": [
            {
                "date": r.get("timestamp"),
                "medicine": r.get("medicine"),
                "drap_mrp": r.get("drap_mrp_now"),
                "charged": r.get("chargedPrice"),
                "overcharge_pct": r.get("verified_overcharge_pct"),
                "drap_reg_number": r.get("drap_reg_number"),
            }
            for r in verified_only
        ],
    }

    enforcement_section = {
        "heading": "Pharmacy Enforcement History (DRAP records)",
        "rows": [
            {
                "date": e.get("violation_date"),
                "violation_type": e.get("violation_type"),
                "description": e.get("description"),
                "penalty": e.get("penalty_type"),
                "penalty_amount_pkr": e.get("penalty_amount_pkr"),
                "drap_notice_ref": e.get("drap_notice_ref"),
                "source_url": e.get("source_url"),
                "severity": e.get("severity"),
            }
            for e in enforcement
        ],
    }

    request_section = {
        "heading": "Request for Action",
        "paragraphs": [
            f"This dossier represents {len(verified_only)} independent, anonymously-submitted "
            f"overcharge reports against {pharmacy_name}, each cross-checked against the current "
            f"DRAP-registered Maximum Retail Price. The pattern of conduct documented here, "
            f"combined with the pharmacy's prior enforcement history above, supports a coordinated "
            f"DRAP investigation under §28 of the DRAP Act 2012.",
            "We respectfully request a formal inspection and the imposition of escalated "
            "penalties consistent with repeat-offender provisions.",
        ],
    }

    return {
        "addressee": "The Director, Drug Regulatory Authority of Pakistan, Islamabad",
        "subject": f"Collective Complaint Dossier — {pharmacy_name}, {pharmacy_full}",
        "letter_date": date.today().isoformat(),
        "pharmacy": {
            "id": pharmacy_id,
            "name": pharmacy_name,
            "area": pharmacy_area,
            "city": pharmacy_city,
        },
        "stats": {
            "total_reports": len(raw_reports),
            "verified_incidents": len(verified_only),
            "medicines_involved": medicines,
            "avg_overcharge_pct": avg_overcharge,
            "enforcement_count": len(enforcement),
        },
        "sections": {
            "summary": summary_section,
            "incidents": incidents_section,
            "enforcement": enforcement_section,
            "request": request_section,
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }

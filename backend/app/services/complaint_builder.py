"""Compose a structured DRAP complaint letter from investigation evidence.

The output is a JSON-serializable dict — no PDF binary here. The agent
returns this directly; the frontend POSTs it back to /complaint/pdf to get
the actual PDF bytes.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

ADDRESSEE = "The Director, Drug Regulatory Authority of Pakistan, Islamabad"


def compose_complaint(
    *,
    pharmacy_name: str,
    pharmacy_city: str,
    pharmacy_area: str | None,
    medicine_name: str,
    strength: str | None,
    drap_reg_number: str,
    active_ingredient: str | None,
    manufacturer: str | None,
    official_mrp_pkr: float,
    charged_price_pkr: float,
    incident_date: str,
    complainant_name: str | None = None,
    prior_violations_summary: str | None = None,
) -> dict[str, Any]:
    overcharge_amt = round(charged_price_pkr - official_mrp_pkr, 2)
    overcharge_pct = round((overcharge_amt / official_mrp_pkr) * 100, 1) if official_mrp_pkr else 0.0
    is_anonymous = not complainant_name
    today = date.today().isoformat()

    pharmacy_full = ", ".join(p for p in [pharmacy_area, pharmacy_city] if p)

    body_sections = [
        {
            "heading": "Complaint",
            "paragraphs": [
                f"I am filing a formal complaint under the Drug Regulatory Authority of "
                f"Pakistan Act, 2012 against {pharmacy_name}, {pharmacy_full}, for charging a "
                f"price in excess of the legally-binding Maximum Retail Price (MRP) registered "
                f"with DRAP."
            ],
        },
        {
            "heading": "Incident Details",
            "paragraphs": [
                f"Date of incident: {incident_date}",
                f"Pharmacy: {pharmacy_name}, {pharmacy_full}",
                f"Medicine: {medicine_name} {strength or ''}".strip(),
                f"Manufacturer: {manufacturer or 'not on record'}",
                f"DRAP registration number: {drap_reg_number}",
                f"Active ingredient: {active_ingredient or 'not on record'}",
            ],
        },
        {
            "heading": "Evidence of Overcharge",
            "paragraphs": [
                f"Official DRAP-registered MRP: Rs. {int(official_mrp_pkr):,}",
                f"Price charged by pharmacy: Rs. {int(charged_price_pkr):,}",
                f"Overcharge: Rs. {int(overcharge_amt):,} ({overcharge_pct}% above MRP)",
                "MRP source: DRAP Medicine Registration Portal (drap.gov.pk/medicine-prices).",
            ],
        },
    ]

    if prior_violations_summary:
        body_sections.append(
            {
                "heading": "Pharmacy Enforcement History",
                "paragraphs": [prior_violations_summary],
            }
        )

    body_sections.append(
        {
            "heading": "Request for Action",
            "paragraphs": [
                "I respectfully request DRAP to investigate this incident under §28 of the "
                "DRAP Act 2012 (sale above maximum retail price), impose appropriate penalties "
                "as provided under the Act, and publish the outcome on the DRAP enforcement "
                "register.",
                "All evidence above is drawn from publicly-available DRAP records and is "
                "verifiable against the registration number cited.",
            ],
        }
    )

    citations = [
        {"label": "DRAP MRP for this medicine", "source": "https://www.drap.gov.pk/medicine-prices"},
        {"label": "DRAP Act 2012 (full text)", "source": "https://www.drap.gov.pk/legal/drap-act-2012"},
    ]

    return {
        "addressee": ADDRESSEE,
        "subject": f"Complaint of Overcharging — {pharmacy_name}, {pharmacy_full}",
        "letter_date": today,
        "complainant_name": complainant_name,
        "is_anonymous": is_anonymous,
        "body_sections": body_sections,
        "citations": citations,
        "incident": {
            "pharmacy_name": pharmacy_name,
            "pharmacy_city": pharmacy_city,
            "pharmacy_area": pharmacy_area,
            "medicine_name": medicine_name,
            "strength": strength,
            "drap_reg_number": drap_reg_number,
            "official_mrp_pkr": official_mrp_pkr,
            "charged_price_pkr": charged_price_pkr,
            "overcharge_amt_pkr": overcharge_amt,
            "overcharge_pct": overcharge_pct,
            "incident_date": incident_date,
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }

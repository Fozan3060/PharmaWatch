from __future__ import annotations

from app.agent.tools.base import tool
from app.services.complaint_builder import compose_complaint


@tool(
    name="generate_complaint_letter",
    description=(
        "Generate a formal, pre-filled DRAP complaint letter from the investigation findings. "
        "Call this AFTER drap_price_lookup has confirmed an overcharge and (ideally) "
        "drap_enforcement_lookup has surfaced any prior violations. Returns structured letter "
        "content ready for PDF rendering — the frontend posts the result back to /complaint/pdf "
        "to get the downloadable file."
    ),
    parameters={
        "type": "object",
        "properties": {
            "pharmacy_name": {"type": "string"},
            "pharmacy_city": {"type": "string"},
            "pharmacy_area": {"type": "string"},
            "medicine_name": {"type": "string"},
            "strength": {"type": "string"},
            "drap_reg_number": {"type": "string", "description": "DRAP registration number from drap_price_lookup."},
            "active_ingredient": {"type": "string"},
            "manufacturer": {"type": "string"},
            "official_mrp_pkr": {"type": "number"},
            "charged_price_pkr": {"type": "number"},
            "incident_date": {"type": "string", "description": "ISO YYYY-MM-DD date of the overcharge."},
            "complainant_name": {
                "type": "string",
                "description": "Optional. Omit to file anonymously (default).",
            },
            "prior_violations_summary": {
                "type": "string",
                "description": "Optional 2-3 sentence summary of prior DRAP enforcement actions, citing notice references.",
            },
        },
        "required": [
            "pharmacy_name",
            "pharmacy_city",
            "medicine_name",
            "drap_reg_number",
            "official_mrp_pkr",
            "charged_price_pkr",
            "incident_date",
        ],
    },
)
def generate_complaint_letter(
    pharmacy_name: str,
    pharmacy_city: str,
    medicine_name: str,
    drap_reg_number: str,
    official_mrp_pkr: float,
    charged_price_pkr: float,
    incident_date: str,
    pharmacy_area: str | None = None,
    strength: str | None = None,
    active_ingredient: str | None = None,
    manufacturer: str | None = None,
    complainant_name: str | None = None,
    prior_violations_summary: str | None = None,
) -> dict:
    return compose_complaint(
        pharmacy_name=pharmacy_name,
        pharmacy_city=pharmacy_city,
        pharmacy_area=pharmacy_area,
        medicine_name=medicine_name,
        strength=strength,
        drap_reg_number=drap_reg_number,
        active_ingredient=active_ingredient,
        manufacturer=manufacturer,
        official_mrp_pkr=official_mrp_pkr,
        charged_price_pkr=charged_price_pkr,
        incident_date=incident_date,
        complainant_name=complainant_name,
        prior_violations_summary=prior_violations_summary,
    )

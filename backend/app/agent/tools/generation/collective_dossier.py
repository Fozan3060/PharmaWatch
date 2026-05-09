from __future__ import annotations

from app.agent.tools.base import tool
from app.services.dossier_builder import compose_dossier


@tool(
    name="generate_collective_dossier",
    description=(
        "Build a bulk DRAP complaint dossier from all community reports for a pharmacy "
        "(verified against current DRAP MRP) plus the pharmacy's prior enforcement history. "
        "Call this when get_pharmacy_reports returns 10+ reports (classification: confirmed) — "
        "this is what makes a single ignorable complaint into an unanswerable case file. "
        "Returns structured content for PDF rendering at /dossier/pdf."
    ),
    parameters={
        "type": "object",
        "properties": {
            "pharmacy_name": {"type": "string"},
            "pharmacy_city": {"type": "string"},
            "pharmacy_area": {"type": "string"},
        },
        "required": ["pharmacy_name", "pharmacy_city"],
    },
)
def generate_collective_dossier(
    pharmacy_name: str,
    pharmacy_city: str,
    pharmacy_area: str | None = None,
) -> dict:
    return compose_dossier(
        pharmacy_name=pharmacy_name,
        pharmacy_city=pharmacy_city,
        pharmacy_area=pharmacy_area,
    )

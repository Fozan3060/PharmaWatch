from __future__ import annotations

from app.agent.tools.base import tool
from app.data.drap.repository import find_medicine_by_brand, search_medicines_like
from app.normalization.medicine_names import normalize, normalize_strength


@tool(
    name="drap_price_lookup",
    description=(
        "Look up the official DRAP-registered Maximum Retail Price (MRP), active ingredient, "
        "and manufacturer for a medicine. Always call this BEFORE web_search_fallback for any "
        "price/MRP question — the local DRAP database is the canonical source."
    ),
    parameters={
        "type": "object",
        "properties": {
            "medicine_name": {
                "type": "string",
                "description": "Brand or generic name as the user wrote it (e.g. 'Ceftum', 'Augmentin').",
            },
            "strength": {
                "type": "string",
                "description": "Dosage strength like '500mg', '625mg', '10ml'. Optional but improves match.",
            },
        },
        "required": ["medicine_name"],
    },
)
def drap_price_lookup(medicine_name: str, strength: str | None = None) -> dict:
    name = normalize(medicine_name)
    strength_norm = normalize_strength(strength)

    exact = find_medicine_by_brand(name, strength_norm)
    if exact:
        return {"found": True, **exact}

    candidates = search_medicines_like(name, limit=3)
    if candidates:
        return {
            "found": False,
            "reason": "no_exact_match",
            "queried": {"medicine_name": medicine_name, "strength": strength},
            "did_you_mean": [
                {"brand_name": c["brand_name"], "strength": c["strength"], "mrp_pkr": c["mrp_pkr"]}
                for c in candidates
            ],
        }

    return {
        "found": False,
        "reason": "not_in_drap_database",
        "queried": {"medicine_name": medicine_name, "strength": strength},
    }

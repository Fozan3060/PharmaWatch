from __future__ import annotations

from app.agent.tools.base import tool
from app.data.drap.repository import find_generics_by_ingredient
from app.normalization.medicine_names import normalize_strength


@tool(
    name="generic_alternatives",
    description=(
        "Find DRAP-registered medicines containing the same active ingredient at lower prices. "
        "Returns up to 5 cheapest alternatives sorted ascending by MRP. All results are "
        "DRAP-registered, legally sold, and contain the same molecule at the same dosage."
    ),
    parameters={
        "type": "object",
        "properties": {
            "active_ingredient": {
                "type": "string",
                "description": "Active ingredient name (e.g. 'Cefuroxime', 'Paracetamol').",
            },
            "strength": {
                "type": "string",
                "description": "Dosage strength to match (e.g. '500mg').",
            },
            "exclude_reg_number": {
                "type": "string",
                "description": "DRAP registration number to exclude (the original branded medicine).",
            },
        },
        "required": ["active_ingredient"],
    },
)
def generic_alternatives(
    active_ingredient: str,
    strength: str | None = None,
    exclude_reg_number: str | None = None,
) -> dict:
    results = find_generics_by_ingredient(
        active_ingredient=active_ingredient,
        strength=normalize_strength(strength),
        exclude_reg_number=exclude_reg_number,
        limit=5,
    )
    return {
        "count": len(results),
        "alternatives": [
            {
                "brand_name": r["brand_name"],
                "manufacturer": r["manufacturer"],
                "mrp_pkr": r["mrp_pkr"],
                "reg_number": r["reg_number"],
                "strength": r["strength"],
            }
            for r in results
        ],
    }

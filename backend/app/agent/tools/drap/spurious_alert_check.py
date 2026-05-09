from __future__ import annotations

from app.agent.tools.base import tool
from app.data.drap.repository import find_spurious_alerts


@tool(
    name="spurious_alert_check",
    description=(
        "Check whether DRAP has issued a counterfeit, substandard, or mislabeled medicine alert "
        "matching the queried medicine (and batch number, if provided). Call this on every "
        "medicine query — even if the price was within the legal MRP."
    ),
    parameters={
        "type": "object",
        "properties": {
            "medicine_name": {
                "type": "string",
                "description": "Medicine brand or generic name to check.",
            },
            "batch_number": {
                "type": "string",
                "description": "Batch number printed on the medicine packaging, if available.",
            },
        },
        "required": ["medicine_name"],
    },
)
def spurious_alert_check(medicine_name: str, batch_number: str | None = None) -> dict:
    alerts = find_spurious_alerts(medicine_name, batch_number)
    return {
        "alert": bool(alerts),
        "count": len(alerts),
        "alerts": [
            {
                "reason": a["reason"],
                "alert_date": a["alert_date"],
                "batch_number": a["batch_number"],
                "drap_notice_ref": a["drap_notice_ref"],
                "source_url": a["source_url"],
            }
            for a in alerts
        ],
    }

"""web_search_fallback — last-resort tool, NOT for prices.

DRAP-first principle: the local SQLite Golden Source is canonical for prices,
generics, spurious alerts, and pharmacy enforcement. Web search is reserved
for fresh news context not yet in our local DB (e.g. an enforcement notice
issued in the last 48 hours).

The tool is configured graceful: if no search backend key is present, it
returns honest "not configured" so the agent can fall back to its other
tools instead of fabricating results.
"""

from __future__ import annotations

import os

from app.agent.tools.base import tool


@tool(
    name="web_search_fallback",
    description=(
        "LAST RESORT. Search the open web for pharmacy enforcement news that may not yet "
        "be in the local DRAP database. NEVER call this for medicine prices, MRPs, generic "
        "alternatives, or spurious-medicine alerts — those have authoritative local tools "
        "(drap_price_lookup, generic_alternatives, spurious_alert_check). Only use this "
        "after drap_enforcement_lookup has returned no results AND you specifically need "
        "very recent news context."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Targeted query, e.g. \"City Pharmacy Saddar Karachi DRAP fine 2025\".",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results to return. Default 5.",
            },
        },
        "required": ["query"],
    },
)
def web_search_fallback(query: str, max_results: int = 5) -> dict:
    api_key = os.getenv("WEB_SEARCH_API_KEY", "")
    if not api_key:
        return {
            "configured": False,
            "results": [],
            "note": (
                "Web search backend not configured for this deployment. "
                "Rely on drap_enforcement_lookup and the local DRAP database."
            ),
        }
    # Real search backend wiring lives behind WEB_SEARCH_API_KEY for Phase 2.
    # Today the agent's enforcement coverage comes from the local SQLite table.
    return {"configured": True, "query": query, "results": [], "note": "backend_stub"}

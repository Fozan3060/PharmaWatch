"""Read-only autocomplete endpoints for the structured investigate form.

These exist so the frontend can:
- only allow medicines that are actually DRAP-registered (the dropdown)
- nudge users toward pharmacies we already know about
"""

from fastapi import APIRouter, Query

from app.data.drap.repository import (
    search_medicines_for_autocomplete,
    search_pharmacies_for_autocomplete,
)

router = APIRouter()


@router.get("/medicines/search")
async def medicines_search(
    q: str = Query(..., min_length=1, max_length=80),
    limit: int = Query(10, ge=1, le=25),
) -> dict:
    rows = search_medicines_for_autocomplete(q, limit=limit)
    return {"results": rows}


@router.get("/pharmacies/known")
async def pharmacies_known(
    q: str = Query(..., min_length=1, max_length=80),
    city: str | None = Query(None, max_length=80),
    limit: int = Query(10, ge=1, le=25),
) -> dict:
    rows = search_pharmacies_for_autocomplete(q, city=city, limit=limit)
    return {"results": rows}

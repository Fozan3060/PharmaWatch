"""PDF download endpoints.

Frontend receives the structured letter/dossier dict from the agent, then
POSTs it back here to get the rendered PDF bytes. Keeps the agent loop
JSON-only and lets the FE control download timing (e.g. on button click).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import Response

from app.services.pdf_renderer import render_complaint_pdf, render_dossier_pdf

router = APIRouter()


@router.post("/complaint/pdf")
async def complaint_pdf(complaint: dict[str, Any]) -> Response:
    pdf = render_complaint_pdf(complaint)
    filename = "pharmawatch-complaint.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/dossier/pdf")
async def dossier_pdf(dossier: dict[str, Any]) -> Response:
    pdf = render_dossier_pdf(dossier)
    pharmacy = dossier.get("pharmacy", {}).get("name", "pharmacy").replace(" ", "-").lower()
    filename = f"pharmawatch-collective-dossier-{pharmacy}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

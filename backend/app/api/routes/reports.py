from fastapi import APIRouter

from app.data.firebase import reports_repo
from app.services.pattern_detection import aggregate_for_heatmap

router = APIRouter()


@router.get("/heatmap")
async def heatmap() -> dict:
    """Initial heatmap load. The frontend subscribes to Firestore directly for live updates."""
    reports = reports_repo.all_recent_reports(days=30)
    return {"pharmacies": aggregate_for_heatmap(reports)}

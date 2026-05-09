from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    db_path = Path(settings.drap_sqlite_path)
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
        "drap_db_present": db_path.exists(),
        "agent_model": settings.gemini_agent_model,
    }

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter

from app.config import get_settings
from app.data.drap.client import get_connection

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
        "data_freshness": _data_freshness() if db_path.exists() else None,
    }


def _data_freshness() -> dict:
    """Latest scrape per table — surfaced in the FE footer as 'data current as of …'."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT table_name, last_scraped_at, row_count FROM scrape_metadata"
        ).fetchall()
    return {r["table_name"]: {"last_scraped_at": r["last_scraped_at"], "row_count": r["row_count"]}
            for r in rows}

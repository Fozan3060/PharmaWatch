from fastapi import APIRouter

router = APIRouter()


@router.get("/heatmap")
async def heatmap():
    # TODO(day 1 evening): aggregate Firestore reports per pharmacy with 30-day window.
    raise NotImplementedError("Heatmap aggregation not wired yet — see Day 1 of PROJECT_PLAN.md")

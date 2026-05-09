from fastapi import APIRouter

from app.api.schemas.agent import InvestigationRequest

router = APIRouter()


@router.post("/investigate")
async def investigate(req: InvestigationRequest):
    # TODO(day 2): wire to app.agent.orchestrator.investigate() with SSE streaming.
    raise NotImplementedError("Agent orchestrator not wired yet — see Day 2 of PROJECT_PLAN.md")

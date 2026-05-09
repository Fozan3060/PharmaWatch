import json
import logging

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.agent import orchestrator
from app.api.schemas.agent import InvestigationRequest

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/investigate")
async def investigate(req: InvestigationRequest):
    """Run the agent and stream every Plan/Tool-Call/Tool-Result/Final event over SSE."""

    async def event_stream():
        try:
            async for trace in orchestrator.investigate(req.user_input):
                yield {
                    "event": trace.type,
                    "id": str(trace.sequence),
                    "data": json.dumps(
                        {"timestamp": trace.timestamp, **trace.data},
                        default=str,
                    ),
                }
        except Exception as exc:
            log.exception("agent stream failed")
            yield {
                "event": "error",
                "data": json.dumps({"reason": "stream_failed", "error": str(exc)}),
            }

    return EventSourceResponse(event_stream())

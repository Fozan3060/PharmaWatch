from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, documents, health, lookup, reports
from app.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="PharmaWatch Agent API",
        version="0.1.0",
        description="Agentic AI for pharmaceutical fraud detection in Pakistan.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(agent.router, prefix="/agent", tags=["agent"])
    app.include_router(reports.router, prefix="/reports", tags=["reports"])
    app.include_router(documents.router, tags=["documents"])
    app.include_router(lookup.router, tags=["lookup"])

    return app


app = create_app()

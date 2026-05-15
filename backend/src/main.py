"""FastAPI entrypoint for the local Goal 4 beta."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.model_routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Goal 4 Market Benchmarking API",
        version="0.1.0",
        description="Local beta API serving benchmark-led Goal 2 price decision payloads.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()

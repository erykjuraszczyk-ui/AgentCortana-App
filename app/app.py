from __future__ import annotations

import os

from fastapi import FastAPI

from app.routers.act import router as act_router

from .middleware.ratelimit import RateLimitMiddleware
from .observability import setup_otel_logging
from .routers.health import router as health_router
from .routers.introspect import router as introspect_router
from .version import __version__, build_meta


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentCortana-App",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Observability
    if os.getenv("OTEL_ENABLED") == "1":
        setup_otel_logging()

    # Rate limiting (config via env; defaults: 5 req / 10s on /act)
    _rl_limit = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
    _rl_window = float(os.getenv("RATE_LIMIT_WINDOW", "10"))
    _rl_paths = {p.strip() for p in os.getenv("RATE_LIMIT_PATHS", "/act").split(",") if p.strip()}
    app.add_middleware(
        RateLimitMiddleware, limit=_rl_limit, window_seconds=_rl_window, paths=_rl_paths
    )

    # Routers
    app.include_router(act_router)
    app.include_router(health_router)
    app.include_router(introspect_router)

    @app.get("/version", tags=["meta"], summary="Service version & build metadata")
    async def version() -> dict[str, str]:
        return {"version": __version__, **build_meta()}

    return app


app = create_app()

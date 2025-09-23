from __future__ import annotations

from fastapi import FastAPI
from .routers.health import router as health_router
from .version import __version__, build_meta


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentCortana-App",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(health_router)

    @app.get("/version", tags=["meta"], summary="Service version & build metadata")
    async def version() -> dict[str, str]:
        return {"version": __version__, **build_meta()}

    return app


app = create_app()

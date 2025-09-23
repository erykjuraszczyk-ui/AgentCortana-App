from fastapi import FastAPI
from .routers.health import router as health_router
app = FastAPI(title="AgentCortana-App", version="0.1.0", docs_url="/docs", redoc_url="/redoc")
app.include_router(health_router)
@app.get("/version", tags=["meta"]) async def version(): return {"version": "0.1.0"}

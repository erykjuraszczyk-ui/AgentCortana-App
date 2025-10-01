from fastapi import FastAPI

from .observability import setup_otel_logging
from .routers import act, meta

setup_otel_logging("agentcortana")

app = FastAPI(title="AgentCortana App")

# rejestracja routerów
app.include_router(meta.router)
app.include_router(act.router)


# opcjonalny root -> 404 w testach nie przeszkadza, ale dodamy przyjazną odpowiedź
@app.get("/")
def root():
    return {"ok": True}

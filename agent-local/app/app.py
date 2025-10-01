from fastapi import FastAPI
from .routers import meta, act
from .observability import setup_otel_logging

setup_otel_logging("agentcortana")

app = FastAPI(title="AgentCortana App")

# rejestracja routerów
app.include_router(meta.router)
app.include_router(act.router)

# opcjonalny root -> 404 w testach nie przeszkadza, ale dodamy przyjazną odpowiedź
@app.get("/")
def root():
    return {"ok": True}

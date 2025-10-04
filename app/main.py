from fastapi import FastAPI

from app.routers.echo import router as echo_router

app = FastAPI(title="AgentCortana API")


@app.get("/health")
def health():
    return {"status": "ok"}


# include routers
app.include_router(echo_router)

from fastapi import FastAPI

app = FastAPI(title="AgentCortana API")


@app.get("/health")
def health():
    return {"status": "ok"}

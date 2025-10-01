from __future__ import annotations
from typing import Any, Literal, Optional
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["act"])

class ActRequest(BaseModel):
    input: str = Field(..., description="User input")
    mode: Optional[Literal["sync", "stream"]] = "sync"

class ActResponse(BaseModel):
    status: Literal["accepted", "unsupported"]
    message: str
    echo: dict[str, Any] | None = None

@router.post("/act", response_model=ActResponse, summary="Agent action (stub)")
async def act(req: ActRequest = Body(...)) -> ActResponse:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")
    return ActResponse(status="accepted", message="Stub only", echo=req.model_dump())


import os, json
from starlette.responses import StreamingResponse

@router.post("/act/stream", summary="Agent action stream (stub)")
async def act_stream(req: ActRequest = Body(...)):
    # walidacja wejścia
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    # feature flag: EXPERIMENTAL_ACT_STREAM
    flag = os.getenv("EXPERIMENTAL_ACT_STREAM", "")
    if str(flag).lower() not in {"1", "true", "yes", "on"}:
        raise HTTPException(status_code=501, detail="streaming not enabled")

    async def gen():
        # minimalny pojedynczy event SSE
        payload = {"status": "accepted", "message": "Stub only (stream)", "echo": req.model_dump()}
        yield "data: " + json.dumps(payload) + "\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

router = APIRouter(tags=["act"])

# singleton, by nie wołać Body(...) w domyślnej wartości parametru (ruff B008)
BODY_REQUIRED = Body(...)


class ActRequest(BaseModel):
    input: str = Field(..., description="User input")
    mode: Literal["sync", "stream"] | None = "sync"


class ActResponse(BaseModel):
    status: Literal["accepted", "unsupported"]
    message: str
    task_id: str | None = None
    accepted_at: str | None = None
    echo: dict[str, Any] | None = None


@router.post("/act", response_model=ActResponse, summary="Agent action (stub)")
async def act(req: ActRequest = BODY_REQUIRED) -> ActResponse:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    # minimalna logika dla trybu sync
    task_id = str(uuid.uuid4())
    ts = datetime.now(UTC).isoformat()

    return ActResponse(
        status="accepted",
        message="Stub only",
        task_id=task_id,
        accepted_at=ts,
        echo=req.model_dump(),
    )


@router.post("/act/stream", summary="Agent action stream (stub)")
async def act_stream(req: ActRequest = BODY_REQUIRED):
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    flag = os.getenv("EXPERIMENTAL_ACT_STREAM", "")
    if str(flag).lower() not in {"1", "true", "yes", "on"}:
        raise HTTPException(status_code=501, detail="streaming not enabled")

    async def gen():
        payload = {
            "status": "accepted",
            "message": "Stub only (stream)",
            "echo": req.model_dump(),
        }
        yield "data: " + json.dumps(payload) + "\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")

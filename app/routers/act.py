from __future__ import annotations

import asyncio
import json
import os
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(tags=["act"])


class ActRequest(BaseModel):
    input: str = Field(..., description="User input")
    mode: Literal["sync", "stream"] = "sync"


class Echo(BaseModel):
    input: str
    mode: Literal["sync", "stream"]


class ActResponse(BaseModel):
    status: Literal["accepted", "unsupported"]
    echo: Echo


@router.post("/act", response_model=ActResponse, summary="Agent action (stub)")
async def act(req: ActRequest) -> ActResponse:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")
    status: Literal["accepted", "unsupported"] = "accepted" if req.mode == "sync" else "unsupported"
    return ActResponse(status=status, echo=Echo(input=req.input, mode=req.mode))


# --- STREAMING (SSE) EXPERIMENTAL -------------------------------------------
@router.post("/act/stream", summary="Agent action (SSE stream, experimental)")
async def act_stream(req: ActRequest):
    """
    Server-Sent Events (SSE) stub. Enable with EXPERIMENTAL_ACT_STREAM=1.
    """
    if os.getenv("EXPERIMENTAL_ACT_STREAM") != "1":
        raise HTTPException(
            status_code=501, detail="stream disabled; set EXPERIMENTAL_ACT_STREAM=1"
        )

    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    async def event_gen():
        for i in range(5):
            payload = {"index": i, "echo": {"input": req.input, "mode": "stream"}}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(event_gen(), media_type="text/event-stream")

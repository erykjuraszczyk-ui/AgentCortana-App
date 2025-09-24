from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
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

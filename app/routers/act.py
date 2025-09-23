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

from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(tags=["meta"])

@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok"}

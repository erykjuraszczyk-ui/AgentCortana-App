import os, json, time, uuid
from typing import Optional, Any, Dict, Iterable
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone

router = APIRouter()

def _extract_text(payload: Dict[str, Any]) -> Optional[str]:
    for key in ("input", "prompt", "text", "message"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

@router.post("/act")
async def act(request: Request):
    """Zwraca status=accepted + task_id(UUID) + timestamp + accepted_at(ISO8601) + echo.input; pusta treść -> 400."""
    try:
        data = await request.json()
    except Exception:
        data = {}
    text = _extract_text(data if isinstance(data, dict) else {})
    if not text:
        raise HTTPException(status_code=400, detail="empty request")
    ts = int(time.time())
    accepted_at = datetime.now(timezone.utc).isoformat()
    return {
        "status": "accepted",
        "task_id": str(uuid.uuid4()),
        "timestamp": ts,
        "accepted_at": accepted_at,
        "echo": {"input": text},
    }

@router.post("/act/stream")
async def act_stream(request: Request):
    """SSE (text/event-stream). Włącz przez EXPERIMENTAL_ACT_STREAM=1; inaczej 501."""
    if os.getenv("EXPERIMENTAL_ACT_STREAM", "0") not in ("1", "true", "True"):
        raise HTTPException(status_code=501, detail="stream disabled")

    try:
        await request.json()
    except Exception:
        pass

    def sse() -> Iterable[bytes]:
        t0 = int(time.time())
        events = [
            {"event": "start", "ts": t0},
            {"event": "chunk", "data": "hello"},
            {"event": "end", "ts": t0 + 1},
        ]
        for e in events:
            yield f"data: {json.dumps(e)}\n\n".encode("utf-8")
            time.sleep(0.01)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(sse(), media_type="text/event-stream", headers=headers)

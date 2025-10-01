from __future__ import annotations

from datetime import datetime
from uuid import UUID

import httpx
import pytest
from httpx import ASGITransport

from app.app import app


@pytest.mark.asyncio
async def test_act_returns_task_and_timestamp():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/act", json={"input": "ping"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "accepted"
    # UUID poprawny
    UUID(body["task_id"])
    # ISO8601 parsowalny
    datetime.fromisoformat(body["accepted_at"])
    assert body["echo"]["input"] == "ping"

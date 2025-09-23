from __future__ import annotations

import httpx
import pytest
from httpx import ASGITransport

from app.app import app


@pytest.mark.asyncio
async def test_introspect_ok():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/introspect")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "AgentCortana-App"
    assert "version" in body and "build" in body and "runtime" in body
    assert isinstance(body["env"], dict)
    assert isinstance(body["packages"], dict)

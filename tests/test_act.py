from __future__ import annotations
import httpx
import pytest
from httpx import ASGITransport
from app.app import app

@pytest.mark.asyncio
async def test_act_stub_accepts():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/act", json={"input": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "accepted"
    assert body["echo"]["input"] == "hello"

@pytest.mark.asyncio
async def test_act_stub_rejects_empty():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/act", json={"input": "   "})
    assert r.status_code == 400

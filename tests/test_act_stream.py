from __future__ import annotations

import os

import httpx
import pytest
from httpx import ASGITransport

from app.app import app


@pytest.mark.asyncio
async def test_act_stream_disabled():
    os.environ.pop("EXPERIMENTAL_ACT_STREAM", None)
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/act/stream", json={"input": "hello", "mode": "stream"})
    assert r.status_code == 501


@pytest.mark.asyncio
async def test_act_stream_enabled_reads_events(monkeypatch):
    monkeypatch.setenv("EXPERIMENTAL_ACT_STREAM", "1")
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/act/stream", json={"input": "hello", "mode": "stream"})
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        text = (await r.aread()).decode()
    # prosty dowód, że to SSE i echo zawiera 'hello'
    assert "data:" in text
    assert "hello" in text

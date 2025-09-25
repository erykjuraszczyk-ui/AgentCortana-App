from __future__ import annotations

import asyncio

import httpx
import pytest
from httpx import ASGITransport

from app.app import create_app


@pytest.mark.asyncio
async def test_rate_limit_blocks_and_recovers(monkeypatch):
    # 3 żądania / 0.2s na /act
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "3")
    monkeypatch.setenv("RATE_LIMIT_WINDOW", "0.2")
    monkeypatch.setenv("RATE_LIMIT_PATHS", "/act")

    test_app = create_app()
    transport = ASGITransport(app=test_app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        for _ in range(3):
            r = await ac.post("/act", json={"input": "hi"})
            assert r.status_code == 200

        r = await ac.post("/act", json={"input": "hi"})
        assert r.status_code == 429

        await asyncio.sleep(0.25)

        r = await ac.post("/act", json={"input": "hi"})
        assert r.status_code == 200

import pytest
from httpx import AsyncClient
from app.app import app
@pytest.mark.asyncio
async def test_health_ok():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
@pytest.mark.asyncio
async def test_version_shape():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body and "python" in body

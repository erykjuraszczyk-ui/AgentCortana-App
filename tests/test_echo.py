from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_echo():
    r = client.post("/v1/echo", json={"message": "hello"})
    assert r.status_code == 200
    assert r.json() == {"echo": "hello"}

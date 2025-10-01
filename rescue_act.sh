#!/usr/bin/env bash
set +e   # nie wychodź przy błędzie
set -x   # pokaż każdy krok
exec 3>run.log
export BASH_XTRACEFD=3
trap 'echo; echo "📜 Log: $(pwd)/run.log"; read -rp "Naciśnij Enter, aby zamknąć..."' EXIT

# 0) Status i gałąź
git status -sb
git switch -c feat/act-stub || git switch feat/act-stub

# 1) Router /act (nadpisze ewentualne śmieci)
mkdir -p app/routers
cat > app/routers/act.py <<'PY'
from __future__ import annotations
from typing import Any, Literal, Optional
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["act"])

class ActRequest(BaseModel):
    input: str = Field(..., description="User input")
    mode: Optional[Literal]["sync", "stream"] | None = "sync"

class ActResponse(BaseModel):
    status: Literal["accepted", "unsupported"]
    message: str
    echo: dict[str, Any] | None = None

@router.post("/act", response_model=ActResponse, summary="Agent action (stub)")
async def act(req: ActRequest = Body(...)) -> ActResponse:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")
    return ActResponse(status="accepted", message="Stub only", echo=req.model_dump())
PY

# 2) Upewnij się, że pakiety są „importowalne”
touch app/__init__.py app/routers/__init__.py

# 3) Podłącz router do aplikacji, jeżeli jest baseline
if [ -f app/app.py ]; then
python - <<'PY'
from pathlib import Path
p = Path("app/app.py")
t = p.read_text()
changed = False
if "from .routers.act import router as act_router" not in t:
    t = t.replace(
        "from .routers.introspect import router as introspect_router",
        "from .routers.introspect import router as introspect_router\nfrom .routers.act import router as act_router"
    )
    changed = True
if "app.include_router(act_router)" not in t and "app.include_router(introspect_router)" in t:
    t = t.replace(
        "app.include_router(introspect_router)",
        "app.include_router(introspect_router)\n    app.include_router(act_router)"
    )
    changed = True
if changed:
    p.write_text(t)
    print("✔ app/app.py zaktualizowany")
else:
    print("ℹ app/app.py już miał /act")
PY
else
  echo "⚠ Brak app/app.py — wygląda na brak baseline’u na tej gałęzi."
fi

# 4) Venv + zależności (z fallbackiem)
python3 -m venv .venv 2>/dev/null || true
. .venv/bin/activate
python -m pip install -q --upgrade pip
if [ -f requirements-dev.txt ]; then
  pip -q install -r requirements-dev.txt
else
  echo "ℹ Brak requirements-dev.txt — instaluję minimalny zestaw do testów"
  pip -q install fastapi pydantic httpx pytest anyio uvicorn
fi

export PYTHONPATH=$(pwd)

# 5) Testy jednostkowe
mkdir -p tests
cat > tests/test_act.py <<'PY'
from __future__ import annotations
import httpx, pytest
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
PY

python -m pytest -q || echo "❌ Testy nie przeszły (szczegóły powyżej i w run.log)"

# 6) Commit + push (push tylko jeśli jest remote 'origin')
git add -A
git commit -m "feat: /act stub (POST) + tests" || echo "ℹ Nic do commitowania"
git remote get-url origin >/dev/null 2>&1 \
  && git push -u origin feat/act-stub \
  || echo "⚠ Brak remote 'origin' — ustaw GH URL i uruchom push ponownie"

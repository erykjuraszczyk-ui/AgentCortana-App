from fastapi import FastAPI
# imports na górze pliku
from typing import Any  # zamiast Dict

from fastapi import HTTPException
from pydantic import BaseModel, Field

# ... reszta importów ...


def embeddings(text: str) -> list[float]:
    try:
        r = requests.post(EMBEDDINGS_URL, json={"inputs": [text]}, timeout=10)
        r.raise_for_status()
        return r.json()["data"][0]["embedding"]
    except Exception as e:
        # B904: pokaż łańcuch wyjątków
        raise HTTPException(status_code=502, detail=f"Embeddings error: {e}") from e


def qdrant_upsert(vec: list[float], payload: dict[str, Any]) -> None:
    body = {
        "points": [{"id": payload.get("id"), "vector": vec, "payload": payload}],
    }
    url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points"
    r = requests.put(url, json=body, timeout=20)
    if r.status_code >= 300:
        # E501: złam linię w nawiasach
        raise HTTPException(
            status_code=502,
            detail=f"Qdrant upsert failed: {r.status_code} {r.text}",
        )


def qdrant_search(vec: list[float], limit: int = 5) -> dict[str, Any] | list[Any]:
    body = {"vector": vec, "limit": limit, "with_payload": True}
    url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search"
    r = requests.post(url, json=body, timeout=20)
    if r.status_code >= 300:
        raise HTTPException(
            status_code=502,
            detail=f"Qdrant search failed: {r.status_code} {r.text}",
        )
    return r.json() or []


def chat(messages: list[dict[str, Any]], temperature: float = 0.2, max_tokens: int = 512) -> str:
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload = {
        "model": "auto",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    url = f"{LLM_BASE_URL}/chat/completions"
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


class RememberReq(BaseModel):
    text: str
    # UP006 + unikaj mutowalnego defaultu
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActReq(BaseModel):
    # … (jak było)
    pass
app = FastAPI()


@app.get("/healthz")
def health():
    st: dict[str, str] = {}
    try:
        requests.get(f"{QDRANT_URL}/collections", timeout=3).raise_for_status()
        st["qdrant"] = "ok"
    except Exception as e:
        st["qdrant"] = f"err:{e}"
    try:
        requests.get(f"{LLM_BASE_URL}/models", timeout=3).raise_for_status()
        st["llm"] = "ok"
    except Exception as e:
        st["llm"] = f"err:{e}"
    try:
        requests.post(EMBEDDINGS_URL, json={"inputs": ["ping"]}, timeout=5).raise_for_status()
        st["embeddings"] = "ok"
    except Exception as e:
        st["embeddings"] = f"err:{e}"
    try:
        m = _minio_client()
        _ensure_bucket(m, MINIO_BUCKET)
        st["minio"] = "ok"
    except Exception as e:
        st["minio"] = f"err:{e}"
    return {"status": st}
@app.post("/remember")
def remember(req: RememberReq) -> dict[str, Any]:
    m = _minio_client()
    _ensure_bucket(m, MINIO_BUCKET)

    obj = f"mem/{int(time.time())}_{uuid.uuid4().hex}.txt"
    data = req.text.encode("utf-8")
    # … reszta jak było …
    return {"ok": True, "object": obj}


import os
import time
import uuid
from typing import Any

import requests

from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8000/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
EMBEDDINGS_URL = os.getenv("EMBEDDINGS_URL", "http://127.0.0.1:8080/embed")
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "mem_default")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "768"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minio")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "agent")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT", "Jesteś pomocnym, precyzyjnym agentem z dostępem do kontekstu RAG."
)


def _minio_client():
    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=MINIO_ENDPOINT.startswith("https://"),
    )


def _ensure_bucket(m: Minio, bucket: str):
    try:
        if not m.bucket_exists(bucket):
            m.make_bucket(bucket)
    except S3Error as e:
        if e.code != "BucketAlreadyOwnedByYou":
            raise


def _qdrant_create():
    r = requests.get(f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}", timeout=5)
    if r.status_code == 200:
        return
    r2 = requests.put(
        f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}",
        json={"vectors": {"size": VECTOR_DIM, "distance": "Cosine"}},
        timeout=10,
    )
    if r2.status_code >= 300:
        raise RuntimeError(f"Qdrant create failed: {r2.status_code} {r2.text}")


def embed(texts: list[str]) -> list[list[float]]:
    try:
        r = requests.post(EMBEDDINGS_URL, json={"inputs": texts}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "data" in data:
            return [d["embedding"] for d in data["data"]]
        if isinstance(data, dict) and "embeddings" in data:
            return data["embeddings"]
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data
        if isinstance(data, dict) and "vector" in data:
            return [data["vector"]]
        raise ValueError("Unexpected embeddings response")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Embeddings error: {e}")


def qdrant_upsert(vec, payload):
    _qdrant_create()
    body = {"points": [{"id": uuid.uuid4().hex, "vector": vec, "payload": payload}]}
    r = requests.put(f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points", json=body, timeout=20)
    if r.status_code >= 300:
        raise HTTPException(
            status_code=502, detail=f"Qdrant upsert failed: {r.status_code} {r.text}"
        )


def qdrant_search(vec, limit=5):
    body = {"vector": vec, "limit": limit, "with_payload": True}
    r = requests.post(
        f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search", json=body, timeout=20
    )
    if r.status_code >= 300:
        raise HTTPException(
            status_code=502, detail=f"Qdrant search failed: {r.status_code} {r.text}"
        )
    return r.json() or []


def chat(messages, temperature=0.2, max_tokens=512):
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    payload = {
        "model": "auto",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(
        f"{LLM_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=120
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]




class RememberReq(BaseModel):
    text: str
    metadata: dict[str, Any] = {}


class ActReq(BaseModel):
    query: str
    top_k: int = 5
    temperature: float = 0.2
    max_tokens: int = 512


@app.get("/health")
def health():
    st = {}
    try:
        requests.get(f"{QDRANT_URL}/collections", timeout=3).raise_for_status()
        st["qdrant"] = "ok"
    except Exception as e:
        st["qdrant"] = f"err:{e}"
    try:
        requests.get(f"{LLM_BASE_URL}/models", timeout=3).raise_for_status()
        st["llm"] = "ok"
    except Exception as e:
        st["llm"] = f"err:{e}"
    try:
        requests.post(EMBEDDINGS_URL, json={"inputs": ["ping"]}, timeout=5).raise_for_status()
        st["embeddings"] = "ok"
    except Exception as e:
        st["embeddings"] = f"err:{e}"
    try:
        m = _minio_client()
        _ensure_bucket(m, MINIO_BUCKET)
        st["minio"] = "ok"
    except Exception as e:
        st["minio"] = f"err:{e}"




def remember(req: RememberReq):
    m = _minio_client()
    _ensure_bucket(m, MINIO_BUCKET)
    obj = f"mem/{int(time.time())}_{uuid.uuid4().hex}.txt"
    data = req.text.encode("utf-8")
    m.put_object(MINIO_BUCKET, obj, data=data, length=len(data), content_type="text/plain")
    vec = embed([req.text])[0]
    qdrant_upsert(
        vec, {"minio_object": obj, "metadata": req.metadata, "text_preview": req.text[:500]}
    )
    return {"ok": True, "object": obj}


@app.post("/act")
def act(req: ActReq):
    qvec = embed([req.query])[0]
    hits = qdrant_search(qvec, limit=req.top_k)
    ctx = []
    for h in hits:
        p = h.get("payload", {})
        ctx.append("- " + (p.get("text_preview") or str(p)))
    ctx_text = "\n".join(ctx) if ctx else "(brak dopasowań)"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + " Używaj kontekstu jeśli pasuje."},
        {"role": "user", "content": f"Zapytanie: {req.query}\n\nKontekst:\n{ctx_text}"},
    ]
    answer = chat(messages, temperature=req.temperature, max_tokens=req.max_tokens)
    return {"answer": answer, "used_context": ctx}

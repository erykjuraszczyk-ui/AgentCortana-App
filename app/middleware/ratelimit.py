from __future__ import annotations

import time
from collections import deque
from collections.abc import Iterable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Prosty limiter w pamięci (per IP)."""

    def __init__(
        self,
        app,
        limit: int = 5,
        window_seconds: float = 10.0,
        paths: Iterable[str] | None = None,
    ):
        super().__init__(app)
        self.limit = int(limit)
        self.window = float(window_seconds)
        self.paths: set[str] = set(paths or [])
        self.buckets: dict[str, deque[float]] = {}

    async def dispatch(self, request: Request, call_next):
        if self.paths and request.url.path not in self.paths:
            return await call_next(request)

        # Klucz: IP z X-Forwarded-For lub socketu
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else "unknown"
        )
        now = time.monotonic()
        cutoff = now - self.window
        dq = self.buckets.setdefault(ip, deque())

        # Usuń stare wpisy
        while dq and dq[0] <= cutoff:
            dq.popleft()

        # Zbyt wiele żądań w oknie
        if len(dq) >= self.limit:
            retry = max(0.0, self.window - (now - dq[0]))
            headers = {
                "Retry-After": str(int(retry) + 1),
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": "0",
            }
            return JSONResponse({"detail": "rate limited"}, status_code=429, headers=headers)

        dq.append(now)
        resp: Response = await call_next(request)
        remaining = max(0, self.limit - len(dq))
        resp.headers.setdefault("X-RateLimit-Limit", str(self.limit))
        resp.headers.setdefault("X-RateLimit-Remaining", str(remaining))
        return resp

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# narzędzia diagnostyczne (curl do HEALTHCHECK, procps dla `ps`)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl procps \
 && rm -rf /var/lib/apt/lists/*

# zależności aplikacji
COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /tmp/requirements.txt

# kod aplikacji
COPY app/ /app/app/

EXPOSE 8000

# HEALTHCHECK po HTTP (FastAPI /health)
HEALTHCHECK --interval=20s --timeout=3s --retries=5 --start-period=10s \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# start uvicorn
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

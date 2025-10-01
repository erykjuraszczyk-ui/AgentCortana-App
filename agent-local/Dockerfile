FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Minimalne runtime-depsy; jeśli masz requirements.txt w agent-local/, dorzuć go później
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir fastapi uvicorn

# Skopiuj kod aplikacji (nasza FastAPI żyje w agent-local/app/)
COPY app/ /app/app/

EXPOSE 8000

# Uruchom serwer
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

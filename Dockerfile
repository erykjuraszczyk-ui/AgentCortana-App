FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# system deps (opcjonalnie, jeśli potrzebujesz curl itp.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -U pip && pip install -r requirements.txt

# skopiuj kod
COPY . .

# domyślne porty/komenda
ENV PORT=8000
CMD ["uvicorn","app.app:app","--host","0.0.0.0","--port","8000"]

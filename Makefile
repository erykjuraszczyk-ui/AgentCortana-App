COMPOSE := $(shell command -v docker-compose >/dev/null 2>&1 && echo docker-compose || echo docker compose)

.PHONY: up up-all down logs bucket test lint db-backup db-restore obj-backup obj-restore

up:
	@if [ ! -f .env.local ]; then cp .env.example .env.local; fi
	$(COMPOSE) --env-file .env.local up -d db minio
	$(MAKE) bucket

up-all:
	@if [ ! -f .env.local ]; then cp .env.example .env.local; fi
	COMPOSE_PROFILES=app $(COMPOSE) --env-file .env.local up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) --env-file .env.local logs -f --tail=200

bucket:
	@set -e
	@if [ ! -f .env.local ]; then echo ".env.local missing"; exit 1; fi
	@set -a; . ./.env.local; set +a; \
	echo "Waiting for MinIO at $$S3_ENDPOINT_URL ..."; \
	until curl -sf "$$S3_ENDPOINT_URL/minio/health/live" >/dev/null; do sleep 1; done; \
	if command -v mc >/dev/null 2>&1; then \
	  mc alias set local "$$S3_ENDPOINT_URL" "$$S3_ACCESS_KEY" "$$S3_SECRET_KEY" >/dev/null 2>&1 || true; \
	  mc mb local/"$$S3_BUCKET" || true; \
	else \
	  aws --endpoint-url "$$S3_ENDPOINT_URL" s3 mb s3://"$${S3_BUCKET}" --no-sign-request >/dev/null 2>&1 || true; \
	fi

lint:
	ruff check --fix . && ruff format .

test:
	pytest -q

db-backup:
	./scripts/db-backup.sh

db-restore:
	./scripts/db-restore.sh

obj-backup:
	./scripts/obj-backup.sh

obj-restore:
	./scripts/obj-restore.sh

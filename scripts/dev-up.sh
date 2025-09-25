#!/usr/bin/env bash
set -euo pipefail
if [ ! -f .env.local ]; then cp .env.example .env.local; fi
${COMPOSE_CMD:-docker compose} --env-file .env.local up -d db minio
make bucket
echo "MinIO console → http://127.0.0.1:9001  (login: $(grep ^S3_ACCESS_KEY .env.local | cut -d= -f2))"

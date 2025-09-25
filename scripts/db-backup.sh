#!/usr/bin/env bash
set -euo pipefail
source .env.local
TS=$(date +"%Y%m%d_%H%M%S")
mkdir -p backups
${COMPOSE_CMD:-docker compose} exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "backups/db_${TS}.sql"
echo "Backup → backups/db_${TS}.sql"

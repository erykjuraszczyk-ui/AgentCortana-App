#!/usr/bin/env bash
set -euo pipefail
FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Użycie: scripts/db-restore.sh backups/db_YYYYmmdd_HHMM.sql"; exit 1; fi
source .env.local
${COMPOSE_CMD:-docker compose} exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$FILE"
echo "Przywrócono z $FILE"

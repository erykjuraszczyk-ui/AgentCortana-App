#!/usr/bin/env bash
set -euo pipefail
source .env.local
mkdir -p backups/objects
if command -v mc >/dev/null 2>&1; then
  mc alias set local "$S3_ENDPOINT_URL" "$S3_ACCESS_KEY" "$S3_SECRET_KEY" >/dev/null 2>&1 || true
  mc mirror --overwrite "local/${S3_BUCKET}" "backups/objects/${S3_BUCKET}"
else
  aws --endpoint-url "$S3_ENDPOINT_URL" s3 sync "s3://${S3_BUCKET}" "backups/objects/${S3_BUCKET}"
fi
echo "Obiekty zarchiwizowane w backups/objects/${S3_BUCKET}"

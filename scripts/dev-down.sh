#!/usr/bin/env bash
set -euo pipefail
${COMPOSE_CMD:-docker compose} down

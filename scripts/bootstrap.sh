#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
EXAMPLE_ENV_FILE="${ROOT_DIR}/.env.example"

log() {
  printf '[bootstrap] %s\n' "$1"
}

fail() {
  printf '[bootstrap] ERROR: %s\n' "$1" >&2
  exit 1
}

command -v docker >/dev/null 2>&1 || fail "docker command not found. Please install Docker Engine + Compose plugin."

docker compose version >/dev/null 2>&1 || fail "docker compose plugin unavailable."

if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ ! -f "${EXAMPLE_ENV_FILE}" ]]; then
    fail ".env.example missing; cannot bootstrap env file."
  fi
  cp "${EXAMPLE_ENV_FILE}" "${ENV_FILE}"
  log "Created .env from .env.example (idempotent copy only when missing)."
else
  log ".env already exists. Skipping copy."
fi

required_vars=(
  ZHIPU_API_KEY
  DEEPSEEK_API_KEY
  DASHSCOPE_API_KEY
  LITELLM_MASTER_KEY
  LITELLM_SALT_KEY
  LITELLM_BASE_URL
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
)

for key in "${required_vars[@]}"; do
  if ! grep -q "^${key}=" "${ENV_FILE}"; then
    fail "${key} is missing in .env"
  fi

  value="$(grep -E "^${key}=" "${ENV_FILE}" | head -n1 | cut -d'=' -f2-)"
  if [[ -z "${value}" ]]; then
    fail "${key} is empty in .env"
  fi
done

log "Starting containers..."
docker compose -f "${ROOT_DIR}/docker-compose.yml" up -d --build

log "Bootstrap finished. Next: run ./scripts/smoke.sh"

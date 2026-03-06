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

if ! grep -q '^OPENAI_API_KEY=' "${ENV_FILE}"; then
  fail "OPENAI_API_KEY is missing in .env"
fi
if grep -q '^OPENAI_API_KEY=sk-your-openai-key$' "${ENV_FILE}"; then
  fail "OPENAI_API_KEY still uses placeholder value."
fi
if ! grep -q '^LITELLM_MASTER_KEY=' "${ENV_FILE}"; then
  fail "LITELLM_MASTER_KEY is missing in .env"
fi
if ! grep -q '^LITELLM_BASE_URL=' "${ENV_FILE}"; then
  fail "LITELLM_BASE_URL is missing in .env"
fi

log "Starting containers..."
docker compose -f "${ROOT_DIR}/docker-compose.yml" up -d --build

log "Bootstrap finished. Next: run ./scripts/smoke.sh"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
BASE_URL="${BASE_URL:-http://localhost}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"

log() {
  printf '[smoke] %s\n' "$1"
}

fail() {
  printf '[smoke] ERROR: %s\n' "$1" >&2
  exit 1
}

command -v curl >/dev/null 2>&1 || fail "curl command not found."
[[ -f "${ENV_FILE}" ]] || fail ".env not found. Run ./scripts/bootstrap.sh first."

# shellcheck disable=SC1090
source "${ENV_FILE}"

: "${LITELLM_MASTER_KEY:?LITELLM_MASTER_KEY not set in .env}"
TEST_API_KEY="${TEST_API_KEY:-$LITELLM_MASTER_KEY}"

curl_json() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local tmp_file
  local status
  tmp_file="$(mktemp)"

  if [[ -n "${data}" ]]; then
    status="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${tmp_file}" -w '%{http_code}' -X "${method}" "${url}" -H 'Content-Type: application/json' -H "Authorization: Bearer ${TEST_API_KEY}" -d "${data}")" || fail "curl failed for ${url}" 
  else
    status="$(curl -sS --max-time "${TIMEOUT_SECONDS}" -o "${tmp_file}" -w '%{http_code}' -X "${method}" "${url}")" || fail "curl failed for ${url}" 
  fi

  if [[ "${status}" -lt 200 || "${status}" -ge 300 ]]; then
    printf '[smoke] ERROR: %s returned HTTP %s\n' "${url}" "${status}" >&2
    cat "${tmp_file}" >&2 || true
    rm -f "${tmp_file}"
    exit 1
  fi

  cat "${tmp_file}"
  rm -f "${tmp_file}"
}

log "1/3 Check control-plane health: ${BASE_URL}/api/healthz"
curl_json GET "${BASE_URL}/api/healthz" >/dev/null

log "2/3 Check LiteLLM readiness via nginx: ${BASE_URL}/health/readiness"
curl_json GET "${BASE_URL}/health/readiness" >/dev/null

log "3/3 Check OpenAI-compatible chat endpoint with test key (TEST_API_KEY or LITELLM_MASTER_KEY)"
CHAT_PAYLOAD='{"model":"router/default-fast","messages":[{"role":"user","content":"Reply with one short word: ok"}],"max_tokens":8}'
RESPONSE="$(curl_json POST "${BASE_URL}/v1/chat/completions" "${CHAT_PAYLOAD}")"

if [[ "${RESPONSE}" != *"choices"* ]]; then
  fail "chat/completions response missing 'choices'. Response: ${RESPONSE}"
fi

log "Smoke checks passed."

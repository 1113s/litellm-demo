# LiteLLM OpenRouter-like Demo (Mono-repo Skeleton)

This repository provides a minimal runnable stack for an OpenRouter-like demo on local machine and Ubuntu 22.04:

- **Nginx** (public entrypoint on port 80)
- **LiteLLM** (gateway on internal port 4000)
- **FastAPI control-plane** (REST + Swagger on internal port 8000)
- **Postgres** (persistent volume)
- **Redis** (persistent volume)

## Architecture (Port Mapping)

- External: `80` (Nginx)
- Internal: `litellm:4000`, `control-plane:8000`

Nginx routing:
- `/v1/*` -> LiteLLM
- `/chat/completions` -> LiteLLM
- `/embeddings` -> LiteLLM
- `/health/readiness` -> LiteLLM readiness
- `/api/*` -> control-plane
- `/docs` and `/openapi.json` -> control-plane Swagger/OpenAPI

## Prerequisites (Ubuntu 22.04)

1. Install Docker Engine.
2. Install Docker Compose plugin (`docker compose version`).
3. Ensure port `80` is open in your firewall/security group.

## Ubuntu 22.04 Deployment Steps

```bash
git clone <your-repo-url> litellm-demo
cd litellm-demo

# idempotent bootstrap: creates .env only if missing, validates required vars, then starts containers
./scripts/bootstrap.sh

# check running services
docker compose ps

# run smoke checks
./scripts/smoke.sh
```

If smoke fails:

```bash
docker compose logs --tail=200 nginx litellm control-plane
```

## Makefile Targets

- `make up` - build and start stack
- `make down` - stop stack and remove volumes
- `make logs` - tail compose logs
- `make test` - run pytest suite
- `make smoke` - run smoke checks
- `make bootstrap` - run idempotent bootstrap script

## Smoke Script Usage

```bash
# default target: http://localhost
./scripts/smoke.sh

# custom base URL + timeout
BASE_URL=http://127.0.0.1 TIMEOUT_SECONDS=30 ./scripts/smoke.sh

# specify dedicated test key (recommended)
TEST_API_KEY=sk-your-virtual-key ./scripts/smoke.sh
```

Smoke checks run in order:
1. `/api/healthz`
2. `/health/readiness`
3. `POST /v1/chat/completions` with `TEST_API_KEY` (or fallback to `LITELLM_MASTER_KEY`)


## Control-plane API Scope

All supported management APIs are under `/api/admin/*` (e.g. tenants/providers/model-catalog/route-policies/keys/usage).

Legacy placeholder routes like `/api/keys` and `/api/models` have been removed to avoid ambiguity.

## Required .env Variables

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `DEEPSEEK_API_KEY`
- `LITELLM_MASTER_KEY`
- `LITELLM_SALT_KEY`
- `LITELLM_BASE_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_HOST`
- `REDIS_PORT`

## Repo Layout

```text
.
├─ docker-compose.yml
├─ .env.example
├─ litellm/config.yaml
├─ deploy/
│  ├─ nginx/
│  └─ control-plane/
├─ control-plane/
├─ db/init/
├─ scripts/
└─ tests/
```

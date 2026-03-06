# LiteLLM OpenRouter-like Demo (Mono-repo Skeleton)

This repository provides a **minimal runnable stack** for an OpenRouter-like demo on local machine and Ubuntu 22.04:

- **Nginx** (public entrypoint on port 80)
- **LiteLLM** (gateway on internal port 4000)
- **FastAPI control-plane** (REST + Swagger on internal port 8000)
- **Postgres** (persistent volume)
- **Redis** (persistent volume)

> Scope in current stage: infrastructure skeleton only. Business logic is intentionally not implemented yet.

## Architecture (Port Mapping)

- External: `80` (Nginx)
- Internal: `litellm:4000`, `control-plane:8000`

Nginx routing:
- `/v1/*` -> LiteLLM
- `/chat/completions` -> LiteLLM
- `/embeddings` -> LiteLLM
- `/api/*` -> control-plane
- `/docs` and `/openapi.json` -> control-plane Swagger/OpenAPI

## Prerequisites (Ubuntu 22.04)

1. Docker Engine
2. Docker Compose plugin (`docker compose version`)

## Quick Start

### 1) Prepare environment variables

```bash
cp .env.example .env
# fill in required values (especially OPENAI_API_KEY / LITELLM_MASTER_KEY)
```

### 2) Start stack

```bash
docker compose up -d --build
```

### 3) Check service status

```bash
docker compose ps
```

### 4) Verify endpoints

```bash
curl http://localhost/
curl http://localhost/api/healthz
curl http://localhost/docs
```

### 5) Optional smoke test

```bash
./scripts/smoke.sh
```

## Compose Service Summary

- `nginx`: reverse proxy entrypoint with route dispatch and healthcheck.
- `litellm`: OpenAI-compatible gateway, started with `litellm/config.yaml`.
- `control-plane`: FastAPI app built from Dockerfile.
- `postgres`: metadata database with init SQL and persistent volume.
- `redis`: cache/state service with persistent volume.

## Required .env Variables

- `OPENAI_API_KEY`
- `LITELLM_MASTER_KEY`
- `LITELLM_SALT_KEY`
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

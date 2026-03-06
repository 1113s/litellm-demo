# LiteLLM OpenRouter-like Demo (Mono-repo Skeleton)

This repository contains a minimal runnable mono-repo skeleton for an OpenRouter-like demo stack:

- **Nginx**: public entrypoint and reverse proxy
- **LiteLLM**: OpenAI-compatible LLM gateway
- **FastAPI control-plane**: REST API + Swagger (`/control/docs`)
- **Postgres**: persistent metadata
- **Redis**: cache / rate-limit state placeholder

> Current stage: infrastructure and project skeleton only. Business logic is intentionally not implemented yet.

## Tech Stack

- Python **3.11**
- FastAPI + SQLAlchemy 2.x + Alembic
- Docker Compose for local and Ubuntu 22.04 deployment

## Quick Start

### 1) Prepare env

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY and other secrets
```

### 2) Start services

```bash
docker compose up -d --build
```

### 3) Verify endpoints

```bash
curl http://localhost/
curl http://localhost/control/healthz
curl http://localhost/control/docs
```

### 4) Optional smoke test

```bash
./scripts/smoke.sh
```

## Exposed Paths

- `GET /` -> nginx gateway banner
- `POST /v1/...` -> proxied to LiteLLM (OpenAI-compatible northbound API)
- `GET /control/healthz` -> FastAPI health check
- `GET /control/docs` -> Swagger UI

## Repo Layout

```text
.
├─ docker-compose.yml
├─ .env.example
├─ deploy/
│  ├─ nginx/
│  ├─ litellm/
│  └─ control-plane/
├─ control-plane/
│  ├─ app/
│  └─ alembic/
├─ db/init/
├─ scripts/
└─ tests/
```

## Ubuntu 22.04 Notes

1. Install Docker Engine + Docker Compose plugin.
2. Clone repo and copy `.env.example` to `.env`.
3. Run `docker compose up -d --build`.
4. Open firewall ports as needed (e.g., `80`).

## Next Steps (not in this commit)

- API key management endpoints and auth
- model mapping CRUD
- usage event ingestion/aggregation
- admin auth and RBAC
- production nginx TLS + rate limits

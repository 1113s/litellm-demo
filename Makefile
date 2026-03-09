.PHONY: up down logs test smoke bootstrap compose-config

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

compose-config:
	docker compose config

test:
	PYTHONPATH=control-plane pytest -q

bootstrap:
	./scripts/bootstrap.sh

smoke:
	./scripts/smoke.sh

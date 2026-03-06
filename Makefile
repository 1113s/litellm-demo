.PHONY: up down logs test compose-config

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

compose-config:
	docker compose config

test:
	docker compose run --rm control-plane pytest -q

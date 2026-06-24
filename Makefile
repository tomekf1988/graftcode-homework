-include .env

GRAFT_REGISTRY_URL ?= https://grft.dev/simple/f812a82c-cdeb-4928-bf7e-c9e6e222e5c2__free

.PHONY: setup test test-inmemory run run-only-pricing

setup:
	uv sync --directory order_service
	VIRTUAL_ENV="" uv pip install --python order_service/.venv/bin/python \
		--index-strategy unsafe-best-match \
		--extra-index-url $(GRAFT_REGISTRY_URL) \
		graft-pypi-pricing-service-graft==0.1.0

test:
	uv run --directory order_service pytest -q

test-inmemory:
	docker cp test_inmemory.py order-graft:/usr/app/test_inmemory.py
	docker exec order-graft python3 /usr/app/test_inmemory.py

run:
	docker compose build order-graft
	docker compose up -d --no-recreate pricing-graft
	docker compose up -d --force-recreate order-graft

run-only-pricing:
	docker compose up -d pricing-graft
	@echo ""
	@echo "Waiting for gg to initialize..."
	@sleep 8
	@echo "Registry URL (copy to GRAFT_REGISTRY_URL in .env):"
	@docker logs pricing-graft 2>&1 | grep -o 'https://grft\.dev/simple/[^[:space:]]*' | tail -1 || \
		echo "(not detected — run: docker logs pricing-graft and look for grft.dev/simple/)"
	@echo ""
	@echo "Then: make setup && make run"

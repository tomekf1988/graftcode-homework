.PHONY: setup test run

setup:
	uv sync --directory order_service
	cd order_service && uv pip install graft-pypi-pricing-service-graft==0.1.0

test:
	uv run --directory order_service pytest -q

run:
	docker compose up -d
	set -a; . ./.env; set +a; uv run --project order_service python -m order_service

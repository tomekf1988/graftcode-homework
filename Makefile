.PHONY: setup test test-inmemory run

setup:
	uv sync --directory order_service
	VIRTUAL_ENV="" uv pip install --python order_service/.venv/bin/python \
		--index-strategy unsafe-best-match \
		--extra-index-url https://grft.dev/simple/f812a82c-cdeb-4928-bf7e-c9e6e222e5c2__free \
		graft-pypi-pricing-service-graft==0.1.0

test:
	uv run --directory order_service pytest -q

test-inmemory:
	docker cp test_inmemory.py order-graft:/usr/app/test_inmemory.py
	docker exec order-graft python3 /usr/app/test_inmemory.py

run:
	docker compose up -d

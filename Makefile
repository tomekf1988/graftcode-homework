.PHONY: setup setup-local test test-inmemory run run-local

PYTHON_VERSION   := $(shell order_service/.venv/bin/python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "3.13")
SITE_PACKAGES    := order_service/.venv/lib/python$(PYTHON_VERSION)/site-packages
GRAFT_PKG_DIR    := $(SITE_PACKAGES)/graft_pypi_pricing_service_graft
GRAFT_MODULE_DIR := $(GRAFT_PKG_DIR)/graft.pricing_service_graft

setup:
	uv sync --directory order_service
	VIRTUAL_ENV="" uv pip install --python order_service/.venv/bin/python \
		--index-strategy unsafe-best-match \
		--extra-index-url https://grft.dev/simple/f812a82c-cdeb-4928-bf7e-c9e6e222e5c2__free \
		graft-pypi-pricing-service-graft==0.1.0

setup-local: setup
	mkdir -p $(GRAFT_MODULE_DIR)
	ln -sfn $(CURDIR)/pricing_service/graft $(GRAFT_MODULE_DIR)/graft

test:
	uv run --directory order_service pytest -q

test-inmemory:
	docker cp test_inmemory.py order-graft:/usr/app/test_inmemory.py
	docker exec order-graft python3 /usr/app/test_inmemory.py

run:
	docker compose up -d

run-local:
	PRICING_MODE=local gg --modules ./order_service/graft/

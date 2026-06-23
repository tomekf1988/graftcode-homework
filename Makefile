.PHONY: setup setup-local test run

PYTHON_VERSION   := 3.13
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

run:
	docker compose up -d
	set -a; . ./.env; set +a; uv run --project order_service python -m order_service

# DONE — Milestone 6

- [x] Write `README.md` — 10 sections: quick start, setup, architecture, configuration, pricing rules, edge cases, error handling, testing, known limitations, versioning
- [x] Update `.env.example` — add `GRAFTCODE_PROJECT_KEY`
- [x] Update milestone status in `docs/milestones/milestone_6_readme_and_docs.md`
- [x] Update CLAUDE.md milestone table

---

# DONE — Milestone 5

- [x] Fix `pricing_service/Dockerfile` CMD — `gg --modules ./pricing_service/graft/` (no `--projectKey`)
- [x] Create `pricing_service/graft/pyproject.toml` — required by `gg` GMA
- [x] Update `docker-compose.yml` — only `pricing-graft` service (port 80/81), order service is local
- [x] Move `pyproject.toml` and `uv.lock` from repo root to `order_service/`
- [x] Add `[[tool.uv.index]]` + `[tool.uv.sources]` to document graft registry in `order_service/pyproject.toml`
- [x] Update `.env.example` — `PRICING_MODE=remote`, `GRAFT_HOST=ws://localhost/ws`
- [x] Create `Makefile` with `setup`, `test`, and `run` targets
- [x] Update imports in `graft_pricing_provider.py` for new package `graft-pypi-pricing-service-graft`
- [x] Delete `main.py`, root `pyproject.toml`, root `uv.lock`, `order_service/Dockerfile`
- [x] All 21 tests pass (`make test`)

---

# DONE — Milestone 4

- [x] Delete `order_service/adapters/local_pricing_provider.py` and `remote_pricing_provider.py`
- [x] Create `order_service/adapters/graft_pricing_provider.py` — reads `GRAFT_HOST`, wraps `PricingServiceGraft`, translates `HypertubeException` → `InvalidOrderRequestError`
- [x] Simplify `order_service/services/order_service.py` — no `pricing_service.*` imports
- [x] Simplify `Settings` to `pricing_mode` only; `GRAFT_HOST` is adapter detail
- [x] Update `factory.py` to create `GraftPricingProvider()` directly
- [x] Update `pyproject.toml` — document graft manual install as comment
- [x] Delete `test_remote_mode.py`, `test_local_provider.py`, `tests/integration/`
- [x] Update `test_factory.py` to patch `GraftPricingProvider`
- [x] Update `test_settings.py` — remove `graft_host` assertions
- [x] Create `test_graft_provider.py` — JSON→PricingQuote mapping, exception translation
- [x] All 29 tests pass (`uv run pytest -q`)

---

# DONE — Milestone 3

- [x] Add `fastapi>=0.115` and `uvicorn[standard]>=0.34` to `pyproject.toml` (runtime)
- [x] Move `pytest` and `httpx` to `[dependency-groups] dev`
- [x] Create `order_service/api/schemas.py` — `PlaceOrderRequest`, `OrderResponse` with `from_result`
- [x] Create `order_service/api/error_handlers.py` — `InvalidOrderRequestError`→400, `OrderNotFoundError`→404, `OrderPlacementError`→503
- [x] Create `order_service/api/routers/orders.py` — `POST /orders` (201), `GET /orders/{order_id}` (200)
- [x] Create `order_service/api/app.py` — FastAPI app + lifespan wiring via `app.state`
- [x] Create `order_service/__main__.py` — uvicorn entry point
- [x] Create `order_service/tests/test_api.py` — 10 tests (all status codes, lifespan smoke test)
- [x] All 36 tests pass (`uv run pytest -q`)

---

# DONE — Milestone 2

- [x] Create `order_service/config/settings.py` — `Settings` dataclass + `load_settings()` (stdlib only)
- [x] `load_settings()` normalises `PRICING_MODE` to lowercase before parsing
- [x] `load_settings()` validates `GRAFTCODE_PROJECT_KEY` is present when `PRICING_MODE=remote`
- [x] Update `order_service/bootstrap/factory.py`: add `create_order_service_from_settings(settings)`
- [x] Rewrite `main.py` as working demo covering 6 scenarios
- [x] Create `.env.example`
- [x] Create `.gitignore`
- [x] Create `order_service/tests/test_settings.py` (6 tests including case-insensitivity)
- [x] All 26 tests pass (`uv run pytest -q`)

---

# DONE — Milestone 1

- [x] Add `UnsupportedCustomerTypeError` to `pricing_service/domain/exceptions.py`
- [x] Add `InvalidOrderRequestError` and `OrderNotFoundError` to `order_service/domain/exceptions.py`
- [x] Fix `LocalPricingProvider`: catch `ValueError` from `CustomerType(...)` → raise `UnsupportedCustomerTypeError`
- [x] Fix `OrderService.place_order`: catch `ProductNotFoundError`, `InvalidQuantityError`, `UnsupportedCustomerTypeError` → wrap in `InvalidOrderRequestError`
- [x] Add in-memory order store (`dict[str, Order]`) to `OrderService`
- [x] Store each placed order in the dict after creation
- [x] Add `get_order(order_id: str) -> OrderResult` method to `OrderService`
- [x] Add structured logging to `pricing_service/services/pricing_service.py`
- [x] Add structured logging to `order_service/services/order_service.py`
- [x] Delete `order_service/tests/test_order_failure.py` (duplicate)
- [x] Update `test_order_service_domain_errors.py` to expect `InvalidOrderRequestError` instead of `ProductNotFoundError`
- [x] Update `test_order_local_validation.py` to expect `InvalidOrderRequestError` instead of `ProductNotFoundError`
- [x] Create `order_service/tests/test_order_service_extended.py` with 5 new tests
- [x] Create `order_service/tests/integration/test_order_get_local.py`
- [x] Create `order_service/tests/test_local_provider.py`
- [x] All 20 tests pass (`uv run pytest -q`)
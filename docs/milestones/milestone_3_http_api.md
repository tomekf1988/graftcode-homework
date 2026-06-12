# Milestone 3 — HTTP API on Order Service (FastAPI)

## Status: done

## Scope

- Dependencies: `fastapi>=0.115`, `uvicorn[standard]>=0.34`, `httpx>=0.27` (dev)
- `order_service/api/app.py` — FastAPI app + lifespan
- `order_service/api/routers/orders.py` — `POST /orders`, `GET /orders/{order_id}`
- `order_service/api/schemas.py` — Pydantic `PlaceOrderRequest` / `OrderResponse`
- `order_service/api/error_handlers.py` — exception → HTTP status code mapping
- `order_service/__main__.py` — `uvicorn.run` entry point
- `order_service/tests/test_api.py` — 10 tests via FastAPI `TestClient`

## Decisions

### `InvalidOrderRequestError` → 400, not 422
FastAPI uses 422 exclusively for Pydantic schema validation failures (wrong type, missing field). Business-layer rejections (unknown product, zero quantity, unsupported customer type) are semantically different: the JSON is valid, the domain rejected it. Mapping them to 400 keeps the two error categories distinguishable for clients.

### `pytest` and `httpx` moved to `[dependency-groups] dev`
They are test-only tools and should not ship in the production image. `uv sync` still installs them locally; `uv sync --no-dev` will omit them in Docker.

### `OrderResponse.from_result` classmethod
Both route handlers previously duplicated the same six-field constructor call. A `from_result` classmethod on `OrderResponse` eliminates the duplication and makes it a single place to update if `OrderResult` grows.

### Lifespan wires `OrderService` via `app.state`
`lifespan()` calls `load_settings()` then `create_order_service_from_settings(settings)` and stores the result in `app.state.order_service`. Route handlers access it via `request.app.state.order_service`. No global state, no DI framework.

### `__main__.py` guard omitted
`order_service/__main__.py` is only executed via `python -m order_service`, so `if __name__ == "__main__":` is redundant noise.

### Test fixture overrides `app.state` after lifespan
The shared `client` fixture sets `app.state.order_service` before entering `TestClient(app)`. The lifespan then overwrites it during `__enter__`. The 503 fake fixture corrects this by setting state *inside* the `with` block, after the lifespan has run. A dedicated `test_lifespan_wires_order_service` test uses `monkeypatch.setenv("PRICING_MODE", "local")` and lets the real lifespan run end-to-end.

## Test coverage

| Test | Asserts |
|------|---------|
| `test_place_order_success` | 201, correct response fields |
| `test_place_order_premium_discount` | premium price < regular price |
| `test_place_order_unknown_product_returns_400` | 400 for unknown product_id |
| `test_place_order_invalid_quantity_returns_400` | 400 for quantity=0 |
| `test_place_order_unknown_customer_type_returns_400` | 400 for unsupported customer type |
| `test_get_order_success` | 200, correct order_id and fields |
| `test_get_order_not_found_returns_404` | 404 for unknown order_id |
| `test_place_order_missing_field_returns_422` | 422 for malformed JSON (Pydantic) |
| `test_pricing_service_unavailable_returns_503` | 503 when pricing provider raises |
| `test_lifespan_wires_order_service` | real lifespan + settings smoke test |

36 tests total (26 existing + 10 new). All pass.

## Notes

Pricing Service does NOT get HTTP endpoints — it remains a pure Python module.
REST exists only between external clients and Order Service, not between services.

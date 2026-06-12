## Summary

Adds a FastAPI HTTP layer to Order Service, making it runnable as a server and testable from any HTTP client. Pricing Service remains a pure Python module called in-process — no HTTP between services. This is the entry point required for Milestone 4 (Docker/Compose).

## Changes

### Backend
- `order_service/api/app.py` — FastAPI app with lifespan that wires `OrderService` via `app.state`
- `order_service/api/dependencies.py` — `get_order_service()` dependency function (used via `Depends`)
- `order_service/api/schemas.py` — `PlaceOrderRequest`, `OrderResponse` with `from_result` classmethod
- `order_service/api/error_handlers.py` — `InvalidOrderRequestError`→400, `OrderNotFoundError`→404, `OrderPlacementError`→503, `PricingServiceUnavailableError`→503 (separate handler)
- `order_service/api/routers/orders.py` — `POST /orders` (201), `GET /orders/{order_id}` (200)
- `order_service/__main__.py` — `uvicorn.run` entry point for `python -m order_service`
- `order_service/tests/test_api.py` — 10 new tests via `TestClient`
- `pyproject.toml` — `fastapi>=0.115`, `uvicorn[standard]>=0.34` as runtime deps; `pytest`, `httpx` moved to `[dependency-groups] dev`

### Frontend
_N/A_

### Infrastructure
- `pytest` and `httpx` moved to `[dependency-groups] dev` — not shipped in production image

## Acceptance criteria

- [x] `POST /orders` → 201 with order JSON
- [x] `GET /orders/{order_id}` → 200 with order JSON
- [x] `InvalidOrderRequestError` → 400
- [x] `OrderNotFoundError` → 404
- [x] `OrderPlacementError` → 503
- [x] `PricingServiceUnavailableError` → 503
- [x] Pydantic schema errors → 422 (FastAPI default, not overridden)
- [x] `fastapi` and `uvicorn[standard]` added to `pyproject.toml`
- [x] `python -m order_service` starts uvicorn on port 8000
- [x] Tests via `TestClient` — 36 total, all pass

## Technical decisions

- **`InvalidOrderRequestError` → 400, not 422** — FastAPI owns 422 for schema validation; domain rejections are semantically different (valid JSON, invalid business request). Clients can distinguish the two.
- **`Depends(get_order_service)` instead of `request.app.state` in routes** — cleaner route signatures, idiomatic FastAPI, enables `app.dependency_overrides` in tests.
- **Separate handlers per exception** — `OrderPlacementError` and `PricingServiceUnavailableError` both return 503 but via their own handlers; coupling them to a single handler was semantically incorrect.
- **`pytest`/`httpx` in dev group** — test tools don't belong in the production dependency set.
- **`from_result` classmethod on `OrderResponse`** — avoids duplicating the six-field mapping across both route handlers.

## Testing

```bash
uv run pytest -q
# 36 passed

PRICING_MODE=local uv run python -m order_service
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'
curl http://localhost:8000/orders/<order_id>
```

## Remaining work

- Milestone 4 — Docker, Docker Compose, Makefile
- Milestone 5 — README & documentation
- Milestone 6 — GraftCode integration (out of scope for now)

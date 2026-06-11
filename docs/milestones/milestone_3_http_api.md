# Milestone 3 — HTTP API on Order Service (FastAPI)

## Status: pending

## Scope

- Dependencies: `fastapi>=0.115`, `uvicorn[standard]>=0.34`
- `order_service/api/app.py` — FastAPI app + lifespan
- `order_service/api/routers/orders.py` — `POST /orders`, `GET /orders/{order_id}`
- `order_service/api/schemas.py` — Pydantic `PlaceOrderRequest` / `OrderResponse`
- `order_service/api/error_handlers.py` — exception → HTTP status code mapping
- `order_service/__main__.py` — `uvicorn.run` entry point
- Tests via FastAPI `TestClient`

## Notes

Pricing Service does NOT get HTTP endpoints — it remains a pure Python module.
REST exists only between external clients and Order Service, not between services.

## Details

See: `docs/plans/pre_graftcode_milestones.md` → Milestone 3.

# PR: Milestone 4 — GraftCode Integration

## Summary

- Replace Local/Remote provider pattern with single `GraftPricingProvider` backed by Graft-generated client
- Remove all `pricing_service.*` imports from `order_service` — clean service boundary enforced
- Simplify `Settings` to `pricing_mode` only; `GRAFT_HOST` is read by the adapter itself
- Fix missing `customer_type` validation in `PricingService.calculate_price`

## Changes

### New files
- `order_service/adapters/graft_pricing_provider.py` — reads `GRAFT_HOST`, maps `HypertubeException` → `InvalidOrderRequestError`, all other exceptions → `PricingServiceUnavailableError`
- `order_service/tests/test_graft_provider.py` — unit tests for the adapter (JSON mapping, exception mapping)

### Deleted files
- `order_service/adapters/local_pricing_provider.py`
- `order_service/adapters/remote_pricing_provider.py`
- `order_service/tests/test_remote_mode.py`
- `order_service/tests/test_local_provider.py`
- `order_service/tests/integration/` (entire directory)

### Updated files
- `order_service/services/order_service.py` — removed `pricing_service.domain.exceptions` import; catch simplified
- `order_service/bootstrap/factory.py` — creates `GraftPricingProvider()` only
- `order_service/config/settings.py` — `pricing_mode` only; no `graft_host`
- `order_service/tests/fakes/product_not_found_pricing_provider.py` — raises `InvalidOrderRequestError`
- `order_service/tests/test_order_service_extended.py` — uses `InvalidOrderRequestError`
- `pricing_service/services/pricing_service.py` — validates `customer_type` upfront
- `pricing_service/tests/test_pricing_service.py` — added test for unsupported customer type

## Test plan

- [x] `uv run pytest -q` — 31 tests pass
- [x] No `pricing_service.*` imports in `order_service` (verified by grep)
- [x] `GraftPricingProvider` tests: JSON→PricingQuote, HypertubeException→InvalidOrderRequestError, Exception→PricingServiceUnavailableError

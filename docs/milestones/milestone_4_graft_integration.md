# Milestone 4 — GraftCode Integration (Architecture Refactor)

## Status: done

## What changed

Replaced the Local/Remote provider pattern with a single `GraftPricingProvider` adapter
backed by the Graft-generated client. Removed all `pricing_service.*` imports from
`order_service`.

### Files deleted
- `order_service/adapters/local_pricing_provider.py`
- `order_service/adapters/remote_pricing_provider.py`
- `order_service/tests/test_remote_mode.py`
- `order_service/tests/test_local_provider.py`
- `order_service/tests/integration/` (entire directory)

### Files created
- `order_service/adapters/graft_pricing_provider.py`
- `order_service/tests/test_graft_provider.py`

### Files changed
- `order_service/services/order_service.py` — removed `pricing_service.domain.exceptions` import
- `order_service/bootstrap/factory.py` — creates `GraftPricingProvider()` directly; no `GraftConfig` touch
- `order_service/config/settings.py` — simplified to `pricing_mode` only; no `graft_host` field
- `order_service/tests/fakes/product_not_found_pricing_provider.py` — raises `InvalidOrderRequestError` (was `ProductNotFoundError`)
- `order_service/tests/test_factory.py` — updated to patch `GraftPricingProvider`
- `order_service/tests/test_settings.py` — removed graft_host assertions
- `order_service/tests/test_order_service_extended.py` — uses `InvalidOrderRequestError` directly
- `pricing_service/services/pricing_service.py` — added `customer_type` validation (bug fix)
- `pricing_service/tests/test_pricing_service.py` — added test for unsupported customer type

## Architecture

```
OrderService (knows only order_service.*)
     │
PricingProvider (protocol, order_service/ports/)
     │
GraftPricingProvider (adapter, order_service/adapters/)
     │  reads GRAFT_HOST env var, sets GraftConfig.host
     ▼
PricingServiceGraft (graft-generated client)
     │
gg Gateway → PricingService (server-side, pricing_service/graft/)
```

### Key decisions

**Zero `pricing_service.*` imports in `order_service`.**
All exception translation happens in `GraftPricingProvider`. `OrderService` knows
only `order_service.domain.exceptions`.

**`GRAFT_HOST` read by the adapter.**
`GraftPricingProvider.__init__` reads `GRAFT_HOST` from env and sets `GraftConfig.host`.
Factory does not touch `GraftConfig`.

**`Settings` simplified to `pricing_mode` only.**
`graft_host` is an adapter implementation detail. `Settings` stays minimal.

**`HypertubeException` → `InvalidOrderRequestError`.**
`HypertubeException` means the server responded with a domain error. All other exceptions
mean the server is unreachable → `PricingServiceUnavailableError`.

**Graft package not in `uv` lockfile.**
Custom registry (`https://grft.dev/simple/…`) returns HTML, not PEP 503.
Install manually:
```bash
uv pip install \
  --extra-index-url https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free \
  graft-pypi-graftcode-homework==0.1.0
```

## Known limitations

- **Local mode** (in-memory Graft) doesn't work — bug in Graft alpha
- `PRICING_MODE=local` is accepted but has no effect; all calls go through the Graft client

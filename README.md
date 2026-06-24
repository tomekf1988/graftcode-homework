# GraftCode Homework — Order & Pricing Services

Two cooperating services exposed through Graftcode Vision:

- **Order Service** — accepts orders, calls pricing, returns a priced result. Accessible via Vision at `localhost:81`.
- **Pricing Service** — domain logic for calculating prices. Runs as an internal Docker service; called by Order Service over WebSocket.

## Quick start

**Prerequisites:** Docker.

**First run** (or after restarting pricing-graft):

```bash
# 1. Start pricing-graft and get the registry URL for the client package
make run-only-pricing
# → Registry URL: https://grft.dev/simple/<guid>__free

# 2. Set it in .env
# GRAFT_REGISTRY_URL=https://grft.dev/simple/<guid>__free

# 3. Build order-graft with the new URL and start everything
make run
```

**Subsequent runs** (pricing-graft not restarted, Docker layer cache intact):

```bash
make run
```

Open Vision at **http://localhost:81** and call `place_order` or `get_order`.

## Architecture

```
Vision UI (localhost:81)
  │  WebSocket  ws://localhost:80/ws
  ▼
order-graft container  (ports 80, 81)
  └── OrderServiceGraft
      └── GraftPricingProvider
            │  WebSocket  ws://pricing-graft/ws
            ▼
      pricing-graft container  (internal, no host ports)
        └── PricingServiceGraft
            └── PricingService  (domain logic)
```

## Rebuilding after pricing-graft restart

The client package registry URL is ephemeral — it changes every time pricing-graft restarts.
Docker layer cache normally masks this, but a fresh `--no-cache` build requires an updated URL.

```bash
# 1. Start pricing-graft and print the current registry URL
make run-only-pricing
# → Registry URL: https://grft.dev/simple/<guid>__free

# 2. Update .env
# GRAFT_REGISTRY_URL=https://grft.dev/simple/<guid>__free

# 3. Rebuild and start order-graft
make run
```

`GRAFT_REGISTRY_URL` from `.env` is passed as a Docker build arg to order-graft.
If not set, falls back to the last known URL hardcoded as default in Makefile and Dockerfile.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `PRICING_MODE` | `remote` | `remote` — WebSocket via gg; `local` — Graft inmemory (outside Docker only) |
| `GRAFT_HOST` | `ws://pricing-graft/ws` | WebSocket address of pricing-graft (Docker internal DNS) |
| `GRAFT_REGISTRY_URL` | *(hardcoded fallback)* | pip index URL for `graft-pypi-pricing-service-graft`. Ephemeral — tied to the running gg instance GUID. |

## Makefile targets

| Target | Description |
|---|---|
| `make run` | Start both containers in background |
| `make run-only-pricing` | Start only pricing-graft, print registry URL |
| `make setup` | Install local deps — needed only for `make test` (not required for Docker) |
| `make test` | Run unit tests |
| `make test-inmemory` | Run inMemory graft client test inside order-graft container |

## Pricing rules

The Pricing Service uses the **Strategy pattern** to apply discounts:

- `PricingRule` — protocol with a single `discount_percent(request)` method
- `PricingRulesEngine` — sums discounts from all registered rules, capped at **20%**

| Rule | Trigger | Discount |
|---|---|---|
| `PremiumCustomerRule` | `customer_type == premium` | 10% |
| `BulkOrderRule` | `quantity >= 10` | 5% |

**Available products:** `laptop` (5000), `mouse` (150), `keyboard` (300)

**Valid customer types:** `regular`, `premium`

## Edge cases

- **Financial precision** — all prices use `Decimal`, never `float`.
- **`quantity = 0`** — raises `InvalidQuantityError`
- **Unknown customer type** — raises `UnsupportedCustomerTypeError`
- **Unknown product** — raises `ProductNotFoundError`

## Error handling

```
order_service.domain.exceptions
  └── OrderError  (base)
      ├── InvalidOrderRequestError       (bad product / quantity / customer type)
      │   ├── ProductNotFoundError
      │   ├── InvalidQuantityError
      │   └── UnsupportedCustomerTypeError
      ├── PricingServiceUnavailableError (gateway unreachable)
      ├── OrderPlacementError            (wraps unavailability)
      └── OrderNotFoundError
```

`GraftPricingProvider` maps `HypertubeException.name` to the specific subtype (`ProductNotFoundError` etc.). Unknown names fall back to `InvalidOrderRequestError`.

**Service boundary:** `order_service` imports nothing from `pricing_service.*`. All exception
translation happens inside `GraftPricingProvider`.

**Vision display:** gg alpha reports the base class name (`InvalidOrderRequestError`) in Vision regardless of the actual subtype. The correct type and message are visible in container logs.

## Testing

```bash
make test          # unit tests (no Docker needed)
make test-inmemory # graft client test inside container (requires: make run)
```

## Known limitations

- **Docker inMemory mode is broken.** `PRICING_MODE=local` inside a gg-hosted service triggers a nested hypertube initialization that crashes on any exception with `TypeError: HypertubeException.__init__() missing 2 required positional arguments`. Remote mode (WebSocket) works. See `docs/graftcode/bugs.md`.

- **Vision WebSocket hardcoded to port 80.** Running two gg instances on the same host means only one Vision works. Order Service owns port 80/81; Pricing Service runs without host port mapping. See `docs/graftcode/bugs.md`.

- **Ephemeral registry.** The `grft.dev/simple/<guid>__free` URL changes on every gg restart. Docker layer cache masks this; a fresh `--no-cache` build after restarting pricing-graft will fail until `GRAFT_REGISTRY_URL` is updated. See `docs/graftcode/bugs.md`.

- **Vision displays base exception class.** gg alpha reports `InvalidOrderRequestError` in Vision even when the actual raised type is `ProductNotFoundError`, `InvalidQuantityError`, or `UnsupportedCustomerTypeError`. The Python type is correct — only the Vision UI label is wrong.

## Versioning

The client package (`graft-pypi-pricing-service-graft`) is regenerated by `gg` on startup when the Pricing Service module changes.

- **New optional parameters or return fields** — backward-compatible.
- **Renamed or removed parameters** — breaking change. Add a new method, regenerate the client, migrate callers, remove the old method.
- **Version pinning** — pinned in `Makefile`. Update only after verifying the new client against the running gateway.

# GraftCode Homework — Order & Pricing Services

Two cooperating services:

- **Order Service** — FastAPI HTTP API that accepts orders, calls pricing, and returns a priced result
- **Pricing Service** — domain logic for calculating prices, exposed over WebSocket via the GraftCode `gg` gateway

## Quick start

**Prerequisites:** Docker.

1. Copy the example env file:

```bash
cp .env.example .env
```

2. Install dependencies (first time only) and start both services:

```bash
make setup   # remote mode (Docker + WebSocket)
make run
```

`make run` starts the `pricing-graft` Docker container (ports 80 and 81) and then launches the Order Service locally on port 8000.

**Local mode (no Docker):**

```bash
make setup-local          # installs deps + wires inmemory Graft
PRICING_MODE=local uv run --project order_service python -m order_service
```

3. Run the test suite:

```bash
make test
```

## Setup

### Configure `.env`

```env
PRICING_MODE=remote
GRAFT_HOST=ws://localhost/ws
```

The `gg` gateway runs locally in Docker and does not require a GraftCode portal account for local development. If you connect to a hosted GraftCode environment, set `GRAFTCODE_PROJECT_KEY` in `.env` and pass it to the container via `docker-compose.yml`.

## Architecture

```
HTTP client
  │  POST /orders
  ▼
Order Service  (FastAPI, :8000)
  │  PricingProvider protocol
  ▼
GraftPricingProvider  (adapter)
  │  WebSocket  (GRAFT_HOST)
  ▼
gg Gateway  (:80)
  │
  ▼
PricingServiceGraft  (server-side Graft module)
  │
  ▼
PricingService  (domain logic)
```

### Why Graft instead of REST between services?

GraftCode generates a typed Python client (`PricingServiceGraft`) directly from the server-side Python method signature. No OpenAPI spec, no manual schema maintenance — the contract is the method. The `gg` gateway handles WebSocket framing, serialisation, and routing transparently. Adding a new pricing method requires only regenerating the client package.

### LOCAL vs REMOTE mode

`PRICING_MODE` controls how the order service resolves prices.

- **`remote`** (default) — calls go through the `gg` gateway over WebSocket. Requires Docker (`make run`).
- **`local`** — Graft inmemory mode: the pricing implementation runs in-process, no Docker or network needed. Requires `make setup-local`.

In local mode `GraftConfig.host` stays at its default `"inmemory"`. Hypertube loads
`pricing_service/graft/pricing_service_graft.py` via a symlink wired by `make setup-local`:

```
# pricingservicegraft.py (Graft-generated client) looks up:
cls._ctx.get_type("graft.pricing_service_graft.PricingServiceGraft")

# setup-local creates:
graft.pricing_service_graft/
  graft  →  pricing_service/graft/    ← symlink so import graft.pricing_service_graft resolves
```

`pricing_service.*` imports work because the repo root is in `sys.path` when the
order service is launched from the repo root via `uv run`.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `PRICING_MODE` | `remote` | `remote` — WebSocket via `gg` gateway; `local` — Graft inmemory (no Docker) |
| `GRAFT_HOST` | `ws://localhost/ws` | WebSocket address of the `gg` gateway (remote mode only) |
| `GRAFTCODE_PROJECT_KEY` | — | Optional. Required only when connecting to a hosted GraftCode environment. |

## Pricing rules

The Pricing Service uses the **Strategy pattern** to apply discounts:

- `PricingRule` — protocol with a single `discount_percent(request)` method
- `PricingRulesEngine` — sums discounts from all registered rules, capped at **20%**

| Rule | Trigger | Discount |
|---|---|---|
| `PremiumCustomerRule` | `customer_type == premium` | 10% |
| `BulkOrderRule` | `quantity >= 10` | 5% |

Adding a new rule requires only implementing `PricingRule` and registering it in the engine — no changes to `PricingRulesEngine`.

**Available products:** `laptop` (5000), `mouse` (150), `keyboard` (300)

## Edge cases

- **Financial precision** — all prices use `Decimal`, never `float`. No rounding is applied.
- **`quantity = 0`** — raises `InvalidQuantityError` → HTTP 400
- **Unknown customer type** — raises `UnsupportedCustomerTypeError` → HTTP 400
- **Unknown product** — raises `ProductNotFoundError` → HTTP 400

## Error handling

```
order_service.domain.exceptions
  └── OrderError  (base)
      ├── InvalidOrderRequestError        → HTTP 400  (bad product / quantity / customer type)
      ├── PricingServiceUnavailableError  → HTTP 503  (gateway unreachable)
      └── OrderPlacementError             → HTTP 503  (wraps unavailability)
```

**Service boundary:** `order_service` imports nothing from `pricing_service.*`. All exception translation happens inside `GraftPricingProvider`. `OrderService` only ever sees `order_service.domain.exceptions` types.

## Testing

### Unit tests

```bash
make test
```

### Manual — curl

Happy path:

```bash
curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}' \
  | python3 -m json.tool
```

Error cases:

```bash
# Unknown product → 400
curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "unknown", "quantity": 1, "customer_type": "regular"}'

# Zero quantity → 400
curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 0, "customer_type": "regular"}'

# Unsupported customer type → 400
curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 1, "customer_type": "vip"}'
```

### Vision UI (GraftCode)

Open `http://localhost:81` to test the Pricing Service directly via the GraftCode browser UI while `make run` is active.

## Known limitations

- **Order Service is not exposed through Vision.** The task requires the Order Service to be accessible via Graftcode Vision so `place_order` can be tested visually. In this solution, only the Pricing Service is exposed through Vision (at `:81`). The Order Service is a plain FastAPI server tested via HTTP (`curl` or any HTTP client). Exposing the Order Service through a second `gg` gateway instance would require wiring a separate Graft module for it.

- **Domain error discrimination.** All domain errors from the Pricing Service arrive as `HypertubeException`. `GraftPricingProvider` maps them uniformly to `InvalidOrderRequestError`. Discriminating between specific error types (e.g. unknown product vs bad quantity) is not currently possible with the Graft alpha SDK.

## Versioning and backward compatibility

The client package (`graft-pypi-pricing-service-graft`) is regenerated by `gg` on startup when the Pricing Service module changes.

- **New optional parameters or return fields** — backward-compatible; existing clients continue to work.
- **Renamed or removed parameters** — breaking change. Add a new method alongside the old one, regenerate the client, migrate callers, then remove the old method.
- **Version pinning** — the package version is pinned in `Makefile` (`make setup`). Update only after verifying the new client against the running gateway.
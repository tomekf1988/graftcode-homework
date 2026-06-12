# Plan: Revised Milestones 4, 5, 6

## Context

Original architecture had:
- `LocalPricingProvider` → direct in-process call to `PricingService`
- `RemotePricingProvider` → stub that always raised `ConnectionError`
- `OrderService` importing exceptions from `pricing_service.domain.exceptions` (service boundary violation)
- Milestone 6 (GraftCode) marked as "out of scope"

After installing the Graft-generated client:
- **Remote mode works**: `GraftConfig.host = "ws://localhost/ws"` + `PricingServiceGraft()`
- **Local mode (in-memory)** does not work — bug in Graft alpha
- Graft integration is now in scope — old Milestone 6 absorbed into new Milestone 4

Milestones reorganised:

| # | Name | Status |
|---|------|--------|
| 1 | Domain & business logic | ✅ done |
| 2 | Configuration | ✅ done |
| 3 | HTTP API (FastAPI) | ✅ done |
| **4** | **GraftCode integration (architecture refactor)** | ✅ done |
| **5** | **Docker, Docker Compose, Makefile** | pending |
| **6** | **README & documentation** | pending |

---

## Installing the Graft package

```bash
uv pip install \
  --extra-index-url https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free \
  graft-pypi-graftcode-homework==0.1.0
```

Client-side imports (order service):
```python
from graft_pypi_graftcode_homework.pricingservicegraft import PricingServiceGraft
from graft_pypi_graftcode_homework.graft.pypi.graftcode_homework.graft_config import GraftConfig
```

---

## Target architecture

```
OrderService (knows only order_service.*)
     │
     ▼
PricingProvider (protocol, order_service/ports/)
     │
     ▼
GraftPricingProvider (adapter, order_service/adapters/)
     │  reads GRAFT_HOST env var, sets GraftConfig.host
     ▼
PricingServiceGraft (generated client — graft_pypi_graftcode_homework)
     │ REMOTE: GraftConfig.host = GRAFT_HOST env var
     │ LOCAL:  no host set (in-memory; Graft alpha bug — does not work)
     ▼
gg Gateway → PricingServiceGraft (server-side, pricing_service/graft/)
```

**Key rules:**
- `order_service` has zero imports from `pricing_service.*`
- `GraftPricingProvider` translates Graft errors to `order_service.domain.exceptions`
- `PricingProvider` protocol is kept — enables fakes in tests

---

## Milestone 4: GraftCode integration (architecture refactor) ✅

### Step 1: Investigate Graft exceptions

Run a diagnostic script with `gg` and the Pricing Service running:

```python
from graft_pypi_graftcode_homework.pricingservicegraft import PricingServiceGraft
from graft_pypi_graftcode_homework.graft.pypi.graftcode_homework.graft_config import GraftConfig

GraftConfig.host = "ws://localhost/ws"
service = PricingServiceGraft()

for label, args in [
    ("unknown product", ("unknown_product", 1, "regular")),
    ("quantity=0",      ("laptop", 0, "regular")),
    ("unknown customer",("laptop", 1, "vip")),
]:
    try:
        print(label, "→", service.calculate_price(*args))
    except Exception as e:
        print(label, f"→ {type(e).__module__}.{type(e).__name__}: {e}")
```

**Result**: all domain errors raise `HypertubeException`. `exc.name` is the string
representation of the exception class (not useful for discrimination). `exc.message`
carries the error text. Decision: `HypertubeException` → `InvalidOrderRequestError`,
all other exceptions → `PricingServiceUnavailableError`.

### Step 2: Remove `pricing_service.*` from `order_service`

**Deleted:**
- `order_service/adapters/local_pricing_provider.py`
- `order_service/adapters/remote_pricing_provider.py`

**Changed: `order_service/services/order_service.py`**

Removed import:
```python
from pricing_service.domain.exceptions import (
    ProductNotFoundError,
    InvalidQuantityError,
    UnsupportedCustomerTypeError,
)
```

Simplified catch — adapter handles translation, `OrderService` no longer needs pricing types:
```python
try:
    quote = self._pricing_provider.calculate_price(...)
except PricingServiceUnavailableError as exc:
    raise OrderPlacementError("Unable to place order because pricing service is unavailable.") from exc
# InvalidOrderRequestError propagates naturally
```

### Step 3: New adapter `order_service/adapters/graft_pricing_provider.py`

```python
class GraftPricingProvider(PricingProvider):

    def __init__(self):
        host = os.environ.get("GRAFT_HOST")
        if host:
            GraftConfig.host = host
        self._client = PricingServiceGraft()

    def calculate_price(self, product_id, quantity, customer_type) -> PricingQuote:
        try:
            result_json = self._client.calculate_price(product_id, quantity, customer_type)
            result = json.loads(result_json)
            return PricingQuote(...)
        except HypertubeException as exc:
            raise InvalidOrderRequestError(exc.message) from exc
        except Exception as exc:
            raise PricingServiceUnavailableError("Pricing service is unavailable.") from exc
```

### Step 4: `pyproject.toml`

Custom registry returns HTML, not PEP 503 Simple API — `uv lock` cannot resolve it.
Package documented as a manual install comment:

```toml
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    # Install separately:
    # uv pip install --extra-index-url https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free \
    #     graft-pypi-graftcode-homework==0.1.0
]
```

### Step 5: `settings.py` and `factory.py`

`Settings` simplified to `pricing_mode` only. `GRAFT_HOST` is an adapter detail.

`factory.py` creates `GraftPricingProvider()` directly — no `GraftConfig` import.

### Step 6: Tests

**Deleted:**
- `test_remote_mode.py` (stub test, always ConnectionError)
- `test_local_provider.py`
- `tests/integration/` (used LocalPricingProvider)

**Updated:**
- `test_factory.py` — patches `GraftPricingProvider`
- `test_settings.py` — removed graft_host assertions

**New:**
- `test_graft_provider.py` — mocks `PricingServiceGraft`; covers:
  - JSON → PricingQuote mapping (Decimal from string)
  - Exception mapping → `InvalidOrderRequestError` / `PricingServiceUnavailableError`

---

## Milestone 5: Docker, Docker Compose, Makefile

### `docker-compose.yml`

```yaml
services:
  pricing-graft:
    build:
      context: .
      dockerfile: pricing_service/Dockerfile
    container_name: pricing-graft
    ports:
      - "80:80"
      - "81:81"
    environment:
      GRAFTCODE_PROJECT_KEY: ${GRAFTCODE_PROJECT_KEY}

  order:
    build:
      context: .
      dockerfile: order_service/Dockerfile
    ports:
      - "8000:8000"
    environment:
      PRICING_MODE: remote
      GRAFT_HOST: ws://pricing-graft/ws
    depends_on:
      - pricing-graft
```

`ws://pricing-graft/ws` — Docker internal DNS, port 80 = gg gateway. Verify on first `make run`.

### `pricing_service/Dockerfile` — fix CMD

Current line does not pass project key to `gg`:
```dockerfile
CMD ["sh", "-c", "gg --projectKey \"$GRAFTCODE_PROJECT_KEY\" --modules ./pricing_service/graft/"]
```

### `order_service/Dockerfile`

```dockerfile
FROM python:3.13-slim
WORKDIR /usr/app
COPY . /usr/app/
RUN pip install uv && uv sync --no-dev
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "order_service"]
```

### `.env.example`

```bash
GRAFTCODE_PROJECT_KEY=your_project_key_here
```

### `Makefile`

```makefile
.PHONY: test run

test:
	uv run pytest -q

run:
	docker compose up --build
```

---

## Milestone 6: README & documentation

Sections:

1. **Quick start** — `make run`, prerequisites (Docker, GraftCode account, `.env`)
2. **Setup** — where to get and how to set `GRAFTCODE_PROJECT_KEY`
3. **Architecture** — diagram `OrderService → PricingProvider → GraftPricingProvider → gg → PricingService`;
   why Graft instead of REST between services
4. **Configuration** — env vars: `PRICING_MODE`, `GRAFT_HOST`
5. **Pricing rules** — strategy pattern, `PricingRulesEngine`, configurability, 20% discount cap
6. **Edge cases** — Decimal vs float, quantity=0, unknown customer type, unknown product
7. **Error handling** — exception taxonomy, service boundary (order service has no pricing exceptions)
8. **Testing** — `make test`, curl, Vision UI at `:81`
9. **Known limitations** — local mode broken (Graft alpha bug), domain error translation via HypertubeException
10. **Versioning / backward compatibility** — how to handle Graft method signature changes

---

## End-to-end verification (after Milestone 5)

```bash
# Unit tests
make test

# Start via Docker Compose
cp .env.example .env   # fill in GRAFTCODE_PROJECT_KEY
make run

# Test the endpoint
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'

# Vision UI
open http://localhost:81
```

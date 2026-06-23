# Plan: Milestone 7 — GraftCode local (inmemory) mode

## Goal

Enable switching between two pricing modes via config:
- `PRICING_MODE=remote` — Graft client connects via WebSocket to `gg` in Docker (status quo)
- `PRICING_MODE=local`  — Graft inmemory mode, no Docker, no network

## Technical context

`GraftConfig.host` defaults to `"inmemory"`. In this mode the Graft runtime loads the
server-side implementation in-process instead of connecting over WebSocket.

After `make setup`, the module directory expected by hypertube does not exist:
```
site-packages/graft_pypi_pricing_service_graft/graft.pricing_service_graft/   ← missing
```

## Solution

### 1. Module directory + symlink

Create the module directory and symlink `graft -> pricing_service/graft/` inside it.

The Graft-generated client (`pricingservicegraft.py`) calls:
```python
cls._ctx.get_type("graft.pricing_service_graft.PricingServiceGraft")
```
Hypertube adds `graft.pricing_service_graft/` to `sys.path` and resolves this via
`import graft.pricing_service_graft`. The symlink makes `graft/pricing_service_graft.py`
(= `pricing_service/graft/pricing_service_graft.py`) importable under the correct name.

`pricing_service.*` imports work because the repo root is in `sys.path` (CWD when
running `uv run --project order_service python -m order_service`).

### 2. `PRICING_MODE` switch

`Settings` gets a `pricing_mode` field. The factory passes `host` to
`GraftPricingProvider` only when `pricing_mode == "remote"`. For `local`, `host=None`
leaves `GraftConfig.host` at its default `"inmemory"`.

---

## Code changes

### `order_service/config/settings.py`
```python
_VALID_PRICING_MODES = {"remote", "local"}

@dataclass(frozen=True)
class Settings:
    pricing_mode: str        # "remote" | "local"
    graft_host: str | None   # used only when pricing_mode == "remote"

def load_settings() -> Settings:
    pricing_mode = os.environ.get("PRICING_MODE", "remote").lower()
    if pricing_mode not in _VALID_PRICING_MODES:
        raise ValueError(f"Invalid PRICING_MODE={pricing_mode!r}. ...")
    return Settings(pricing_mode=pricing_mode, graft_host=os.environ.get("GRAFT_HOST"))
```

### `order_service/bootstrap/factory.py`
```python
def create_order_service(settings: Settings) -> OrderService:
    host = settings.graft_host if settings.pricing_mode == "remote" else None
    return OrderService(pricing_provider=GraftPricingProvider(host=host))
```

### `Makefile`
```makefile
PYTHON_VERSION   := $(shell order_service/.venv/bin/python3 -c \
    "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" \
    2>/dev/null || echo "3.13")
SITE_PACKAGES    := order_service/.venv/lib/python$(PYTHON_VERSION)/site-packages
GRAFT_PKG_DIR    := $(SITE_PACKAGES)/graft_pypi_pricing_service_graft
GRAFT_MODULE_DIR := $(GRAFT_PKG_DIR)/graft.pricing_service_graft

setup-local: setup
    mkdir -p $(GRAFT_MODULE_DIR)
    ln -sfn $(CURDIR)/pricing_service/graft $(GRAFT_MODULE_DIR)/graft
```

---

## Tests

- `test_settings.py` — `PRICING_MODE=local` parses correctly; uppercase normalised;
  unknown value raises `ValueError`
- `test_factory.py` — `pricing_mode=local` → `GraftPricingProvider(host=None)`;
  `pricing_mode=remote` → host passed through

---

## Verification

```bash
make setup-local
PRICING_MODE=local uv run --project order_service python -m order_service

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "regular"}'
# {"order_id": "...", "total_price": "10000", "status": "CREATED"}
```

No Docker, no network — pricing runs in-process via Graft inmemory.

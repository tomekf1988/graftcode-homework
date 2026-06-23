# Milestone 7 — GraftCode Local (Inmemory) Mode

## Status: done

## Goal

Enable switching between two pricing modes via config only:

- `PRICING_MODE=remote` — Graft client connects via WebSocket to `gg` in Docker (default)
- `PRICING_MODE=local`  — Graft inmemory mode; no Docker, no network required

## What was built

### `order_service/config/settings.py`
Added `pricing_mode: str` field. `load_settings()` reads `PRICING_MODE` from env,
normalised to lowercase (default `"remote"`).

### `order_service/bootstrap/factory.py`
Passes `host=settings.graft_host` only when `pricing_mode == "remote"`. For `local`,
passes `host=None` — `GraftConfig.host` stays at its default `"inmemory"`.

### `Makefile` — `setup-local` target

Two operations beyond `make setup`:

```makefile
mkdir -p $(GRAFT_MODULE_DIR)
ln -sfn $(CURDIR)/pricing_service/graft $(GRAFT_MODULE_DIR)/graft
```

Result:
```
site-packages/graft_pypi_pricing_service_graft/
  graft/                          ← installed client (unchanged)
  graft.pricing_service_graft/    ← module dir, required by hypertube
    graft  →  pricing_service/graft/    ← symlink
```

## Why this symlink

`pricingservicegraft.py` (Graft-generated client) contains:

```python
cls._ctx.get_type("graft.pricing_service_graft.PricingServiceGraft")
```

Hypertube adds `graft.pricing_service_graft/` to `sys.path` and tries
`import graft.pricing_service_graft`. For that import to resolve, `graft/` must be
a package on that sys.path entry containing `pricing_service_graft.py`.

`pricing_service/graft/` is already a directory named `graft/` containing
`pricing_service_graft.py` — a single symlink makes it importable under the correct
name without copying any files.

`pricing_service.*` imports inside `pricing_service_graft.py` work because the repo
root is always in `sys.path` (CWD when running `uv run --project order_service
python -m order_service`).

## Tests

- `test_settings.py` — `PRICING_MODE=local` parses correctly; uppercase normalised;
  defaults to `"remote"`
- `test_factory.py` — `pricing_mode=local` → `GraftPricingProvider(host=None)`;
  `pricing_mode=remote` → host passed through

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

## See also

`docs/plans/milestone_7_local_mode.md`

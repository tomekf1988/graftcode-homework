## Summary

Introduces environment-based configuration for the Order Service. `load_settings()` reads `PRICING_MODE` and `GRAFTCODE_PROJECT_KEY` from env at startup, validates them, and produces an immutable `Settings` value object. This makes the service deployable with different pricing backends without code changes.

## Changes

### Backend
- `order_service/config/settings.py` — `Settings` frozen dataclass + `load_settings()` (stdlib only: `os`, `dataclasses`)
- `order_service/bootstrap/factory.py` — added `create_order_service_from_settings(settings)` alongside the unchanged `create_order_service(mode)`
- `main.py` — rewritten as a working 6-scenario demo script (happy path, product not found, invalid quantity, unknown customer type, retrieve order, order not found)
- `order_service/tests/test_settings.py` — 6 tests with `monkeypatch` isolation

### Infrastructure
- `.env.example` — documents `PRICING_MODE` and `GRAFTCODE_PROJECT_KEY` with defaults
- `.gitignore` — adds `.env`, `.DS_Store`, `.claude/settings.local.json`, `.venv/`, `__pycache__/`, `.pytest_cache/`

## Acceptance criteria

- [x] `PRICING_MODE` defaults to `local`; accepts `local` and `remote` (case-insensitive)
- [x] Invalid `PRICING_MODE` raises `ValueError` listing valid values
- [x] `GRAFTCODE_PROJECT_KEY` is optional in local mode; required (non-blank) in remote mode
- [x] `create_order_service_from_settings(settings)` wires the service from config
- [x] `main.py` runs end-to-end without errors (`uv run python main.py`)
- [x] All 26 tests pass (`uv run pytest -q`)

## Technical decisions

- **Stdlib only** — no pydantic or python-dotenv; `os` + `dataclasses` are sufficient for two env vars
- **Case-insensitive `PRICING_MODE`** — `.lower()` before enum parsing so `LOCAL`, `local`, and `Local` all work; env vars are idiomatically upper-cased
- **Blank key treated as absent** — `os.environ.get("GRAFTCODE_PROJECT_KEY") or None` so `GRAFTCODE_PROJECT_KEY=` (set but empty) triggers the same error as unset
- **Frozen dataclass** — `Settings` is a value object produced once at startup and never mutated; frozen makes it hashable and prevents accidental reassignment
- **`graftcode_project_key` validated but not injected** — validated at startup for fast-fail, but `RemotePricingProvider` still reads the env var directly; passing the key through the factory is deferred to Milestone 6 when remote mode is fully wired up

## Testing

```bash
uv run pytest -q          # 26 tests, all passing
uv run python main.py     # demo: 6 scenarios printed to stdout
```

## Remaining work

- Milestone 3: HTTP API on Order Service (FastAPI) — `POST /orders`, `GET /orders/{order_id}`, error handlers, uvicorn entry point
- Milestone 4: Docker, Docker Compose, Makefile
- Milestone 5: README & documentation

## PR

https://github.com/tomekf1988/graftcode-homework/pull/2

# Milestone 2 — Configuration

## Status: done

## Scope

- `order_service/config/settings.py` — read `PRICING_MODE`, `GRAFTCODE_PROJECT_KEY` from env
- `order_service/bootstrap/factory.py` — `create_order_service_from_settings` delegates to existing `create_order_service`
- `main.py` — working demo script (6 order scenarios)
- `.env.example` — env variable documentation
- `.gitignore` — added `.env`, `.DS_Store`, `.claude/`, `.pytest_cache/`

## Implementation

### `Settings` dataclass (`order_service/config/settings.py`)

Frozen dataclass with two fields:

- `pricing_mode: PricingMode` — parsed from `PRICING_MODE` env var (default `"local"`); raises `ValueError` listing valid values on an unrecognised string
- `graftcode_project_key: str | None` — read from `GRAFTCODE_PROJECT_KEY`; raises `ValueError` when `PRICING_MODE=remote` and the key is absent or blank

stdlib only (`os`, `dataclasses`). No third-party dependencies.

### Factory (`order_service/bootstrap/factory.py`)

`create_order_service_from_settings(settings: Settings) -> OrderService` added alongside the unchanged `create_order_service(mode)`. The new function reads `settings.pricing_mode` and delegates, keeping the factory composable without breaking existing callers.

Note: `graftcode_project_key` is validated at startup but not yet injected into `RemotePricingProvider` — the remote provider reads the env var directly. Passing the key through is deferred to the milestone that fully wires up the remote provider.

### Demo script (`main.py`)

Six scenarios run in sequence: happy path, product not found, invalid quantity, unknown customer type, retrieve placed order, and order not found. Defaults to LOCAL mode via `load_settings()`.

## Tests

Five tests in `order_service/tests/test_settings.py`, all using `monkeypatch` for full isolation:

1. No env vars set → defaults to `PricingMode.LOCAL`, `graftcode_project_key=None`
2. `PRICING_MODE=remote` + `GRAFTCODE_PROJECT_KEY=test-key` → `PricingMode.REMOTE`
3. `PRICING_MODE=remote`, key absent → `ValueError`
4. `PRICING_MODE=remote`, key blank (`""`) → `ValueError` (blank treated same as absent)
5. `PRICING_MODE=cloud` (invalid) → `ValueError`

Total: 25 tests, all passing.

## Architectural decisions

### Blank `GRAFTCODE_PROJECT_KEY` treated as absent
`os.environ.get("GRAFTCODE_PROJECT_KEY") or None` normalises an empty string to `None`. This means `GRAFTCODE_PROJECT_KEY=` (set but blank) triggers the same `ValueError` as an unset key. Tested explicitly.

### `Settings` is frozen
`@dataclass(frozen=True)` — `Settings` is a value object produced once at startup and never mutated. Frozen makes it hashable and prevents accidental reassignment.

### `PRICING_MODE` is case-insensitive
`os.environ.get("PRICING_MODE", "local").lower()` normalises the value before parsing, so `LOCAL`, `Local`, and `local` all resolve to `PricingMode.LOCAL`. Env vars are idiomatically upper-cased so this avoids a common misconfiguration.

### No `__init__.py` in `order_service/config/`
The `config/` package imports work via the existing package structure without an `__init__.py`. None was added.

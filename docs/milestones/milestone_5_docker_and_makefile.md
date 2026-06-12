# Milestone 5 — Docker, Docker Compose, Makefile

## Status: done

## Deliverables

| File | Action |
|------|--------|
| `pricing_service/Dockerfile` | Updated CMD — no `--projectKey`, `gg` runs on port 80/81 |
| `pricing_service/graft/pyproject.toml` | New — required by `gg` GMA to find Python metadata |
| `docker-compose.yml` | Only `pricing-graft` service (order service is local) |
| `order_service/pyproject.toml` | Moved from repo root; documents graft index via `[[tool.uv.index]]` |
| `order_service/uv.lock` | Moved from repo root |
| `Makefile` | New — `setup`, `test`, `run` targets |
| `.env.example` | `PRICING_MODE=remote` + `GRAFT_HOST=ws://localhost/ws` |
| `order_service/adapters/graft_pricing_provider.py` | Updated imports for new package `graft-pypi-pricing-service-graft` |
| `main.py` | Deleted (dead smoke-test code) |
| `pyproject.toml` (root) | Deleted — moved to `order_service/` |
| `uv.lock` (root) | Deleted — moved to `order_service/` |

## Key decisions

### Only pricing-graft runs in Docker
`gg` generates a new client package each time it analyzes the module. Running the order
service inside Docker would require reinstalling the graft package on every `gg` restart.
Instead: `docker compose up -d` starts only `pricing-graft`; the order service runs locally
via `uv run --project order_service`.

### `pricing_service/graft/pyproject.toml` is required by `gg`
The `gg` GMA (module analyzer) uses `pyproject.toml` to extract package name, version, and
`requires-python`. Without it, `gg` fails with "No metadata source found". Added:
```toml
[project]
name = "pricing-service-graft"
version = "0.1.0"
requires-python = ">=3.13"
```

### `[[tool.uv.index]]` documents the graft registry
The custom registry (`grft.dev/simple/…`) returns HTML, not a PEP 503 Simple API, so
`uv lock` cannot resolve it. The index entry and `[tool.uv.sources]` section exist for
documentation only. `make setup` installs the package separately:
```
cd order_service && uv pip install graft-pypi-pricing-service-graft==0.1.0
```
When `gg` generates a new package, only the URL in `[[tool.uv.index]]` and the version in
`make setup` need updating.

### `pyproject.toml` and `uv.lock` moved to `order_service/`
There is only one Python package (order-service). Keeping project metadata at the repo root
was misleading. All `uv` commands now use `--directory order_service` or `--project order_service`.

### `GRAFT_HOST=ws://localhost/ws`
Order service reaches pricing-graft on `localhost` port 80 (Docker maps 80:80). Docker
internal DNS (`ws://pricing-graft/ws`) is only valid from inside another container.

### `--projectKey` omitted
`gg` works without `--projectKey` for the free tier.

## Makefile

```makefile
setup:
    uv sync --directory order_service
    cd order_service && uv pip install graft-pypi-pricing-service-graft==0.1.0

test:
    uv run --directory order_service pytest -q

run:
    docker compose up -d
    set -a; . ./.env; set +a; uv run --project order_service python -m order_service
```

## Verification

```bash
make setup               # install dependencies (run once)
make test                # 21 tests pass

docker compose up -d     # start pricing-graft (port 80/81)
make run                 # starts order service on :8000

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'
# → 201 {"order_id": "...", "total_price": "9000.0", ...}
```

## See also

`docs/plans/milestone_4_5_6_revised_plan.md` → Milestone 5.

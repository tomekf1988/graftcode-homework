# Milestone 5 — Docker, Docker Compose, Makefile

## Status: pending

## Scope

- `docker-compose.yml` — dwa serwisy: `pricing-graft` + `order`
- `pricing_service/Dockerfile` — poprawka CMD (dodaj `--projectKey`)
- `order_service/Dockerfile` — nowy plik
- `.env.example` — dokumentacja zmiennych środowiskowych
- `Makefile` — targety `test` i `run`

## Szczegóły

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

`GRAFT_HOST: ws://pricing-graft/ws` — Docker internal DNS; port 80 = gg WebSocket gateway.
Do weryfikacji przy pierwszym `make run`.

### `pricing_service/Dockerfile` — poprawka CMD

Obecna linia nie przekazuje project key do `gg`:
```dockerfile
# Przed:
CMD ["gg","--modules","./pricing_service/graft/"]

# Po:
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

`uv sync --no-dev` korzysta z `[[tool.uv.index]]` w `pyproject.toml` (skonfigurowanego w M4),
więc custom registry Graft jest dostępny automatycznie.

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

## Weryfikacja

```bash
cp .env.example .env   # wypełnij GRAFTCODE_PROJECT_KEY
make run

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'

# Vision UI (Pricing Service)
open http://localhost:81
```

## Details

See: `docs/plans/milestone_4_5_6_revised_plan.md` → Milestone 5.

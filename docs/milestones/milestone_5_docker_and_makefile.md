# Milestone 5 — Docker, Docker Compose, Makefile

## Status: pending

## Scope

- `docker-compose.yml` — two services: `pricing-graft` + `order`
- `pricing_service/Dockerfile` — fix CMD to pass `--projectKey`
- `order_service/Dockerfile` — new file
- `.env.example` — env variable documentation
- `Makefile` — `test` and `run` targets

## Details

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

`GRAFT_HOST: ws://pricing-graft/ws` — Docker internal DNS; port 80 is the gg WebSocket gateway.
To be verified on the first `make run`.

### `pricing_service/Dockerfile` — fix CMD

Current line does not pass the project key to `gg`:
```dockerfile
# Before:
CMD ["gg","--modules","./pricing_service/graft/"]

# After:
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

`uv sync --no-dev` uses the custom Graft registry configured in `pyproject.toml`,
so no extra flags are needed.

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

## Verification

```bash
cp .env.example .env   # fill in GRAFTCODE_PROJECT_KEY
make run

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'

# Vision UI (Pricing Service)
open http://localhost:81
```

## See also

`docs/plans/milestone_4_5_6_revised_plan.md` → Milestone 5.

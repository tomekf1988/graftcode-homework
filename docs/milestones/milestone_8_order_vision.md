# Milestone 8 — Order Service przez Vision

## Status: done

## Cel

Wystawić Order Service przez Graftcode Vision jako osobny moduł gg.
Usunąć FastAPI — jedynym wejściem do systemu jest Vision.

---

## Co usunięto

- `order_service/api/` — cały FastAPI (routers, schemas, app, error_handlers, dependencies)
- `order_service/__main__.py`
- `order_service/tests/test_api.py`
- zależności `fastapi`, `httpx` z `order_service/pyproject.toml`

---

## Co dodano

### `order_service/graft/order_service_graft.py`

Klasa `OrderServiceGraft` z metodami `place_order()` i `get_order()`.
W `__init__` woła `load_settings()` → `create_order_service(settings)`.
Zwraca JSON string — analogicznie do `PricingServiceGraft`.

### `order_service/graft/pyproject.toml`

Metadata wymagana przez gg GMA (name, version, requires-python).

### `order_service/graft/Dockerfile`

Instaluje gg + `pip install graft-pypi-pricing-service-graft` z custom registry.
`CMD ["gg", "--modules", "./order_service/graft/"]`

### `.dockerignore`

Wyklucza `.venv`, `__pycache__`, `.git`, `*.pyc` z build context.

### `docker-compose.yml`

```yaml
pricing-graft:
  dockerfile: pricing_service/graft/Dockerfile
  # brak port mappingu na host — serwis wewnętrzny

order-graft:
  dockerfile: order_service/graft/Dockerfile
  ports: 80:80, 81:81        # Vision na localhost:81
  environment:
    PRICING_MODE: ${PRICING_MODE:-remote}
    GRAFT_HOST: ${GRAFT_HOST:-ws://pricing-graft/ws}
  volumes:
    - ./pricing_service/graft:/usr/local/.../graft.pricing_service_graft/graft:ro
  depends_on:
    - pricing-graft
```

### `.env`

Plik do przełączania trybu bez zmiany kodu:
```
PRICING_MODE=remote
GRAFT_HOST=ws://pricing-graft/ws
```

### `test_inmemory.py`

Skrypt do testowania graft klienta w trybie inMemory bezpośrednio w kontenerze (poza gg runtime).
`docker cp test_inmemory.py order-graft:/usr/app/ && docker exec order-graft python3 /usr/app/test_inmemory.py`

---

## Architektura — Remote mode (Docker, domyślny)

```
docker compose up

pricing-graft (wewnętrzny, bez portów na host)
  └── PricingServiceGraft → PricingService
  └── dostępny jako ws://pricing-graft/ws (Docker DNS)

order-graft (porty 80:80, 81:81)
  └── OrderServiceGraft
      └── GraftPricingProvider(host=ws://pricing-graft/ws)
          └── WebSocket → pricing-graft
  └── Vision: localhost:81
```

## Architektura — Local dev (poza Dockerem, bez zmian vs M7)

```
make run-local

gg --modules ./order_service/graft/
  └── OrderServiceGraft
      └── GraftPricingProvider(host=None) → inmemory → symlink → PricingService

Vision: localhost:81
```

---

## Kluczowe odkrycia podczas implementacji

### Vision port 80 hardcoded

Vision JS zawsze łączy się do `ws://localhost:80/ws`. Jeśli order-graft był na porcie 82→80, Vision łączyła się z pricing-graft (port 80) i zwracała błąd `graft.order_service_graft not found`. Bug w gg — szczegóły w `docs/graftcode/bugs.md`.

**Decyzja**: order-graft dostaje port 80/81 (główna Vision), pricing-graft jest serwisem wewnętrznym bez portów na host.

### Docker inMemory mode — nested hypertube bug

Tryb `PRICING_MODE=local` wewnątrz gg-hosted service nie działa: gg inicjalizuje swój Python runtime, a graft klient próbuje zainicjować drugi runtime hypertube → `TypeError: HypertubeException.__init__() missing 2 required positional arguments`.

Graft klient w inMemory mode działa poprawnie poza gg (bezpośredni python3). Szczegóły w `docs/graftcode/bugs.md`.

**Decyzja**: Docker = remote mode only. Local dev = `make run-local` (poza Dockerem).

### Volume mount dla inMemory (pomocniczy)

`docker-compose.yml` ma volume mount `pricing_service/graft` → GMA dir. Nie pomaga z nested hypertube bug, ale umożliwia testowanie graft klienta bezpośrednio w kontenerze (`test_inmemory.py`).

---

## Tryby działania

| Tryb | Jak uruchomić | Status |
|------|--------------|--------|
| Docker remote | `docker compose up` | ✅ działa |
| Docker local | `PRICING_MODE=local docker compose up` | ❌ nested hypertube bug |
| Local non-Docker | `make run-local` | ✅ działa |

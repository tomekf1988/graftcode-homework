# Milestone 8 — Order Service przez Vision (remote mode)

## Status: planned

## Cel

Wystawić Order Service przez Graftcode Vision jako osobny moduł gg.
Usunąć FastAPI — jedynym wejściem do systemu jest Vision.

Scope tego milestone: **tryb remote** (dwa kontenery, WebSocket).
Symlinki w Dockerze dla trybu local — odkładamy na później.

---

## Co usuwamy

- `order_service/api/` — cały FastAPI (routers, schemas, app, error_handlers, dependencies)
- `order_service/__main__.py`
- `order_service/tests/test_api.py`
- zależności `fastapi`, `httpx` z `order_service/pyproject.toml`

---

## Co dodajemy

### `order_service/graft/order_service_graft.py`

Klasa `OrderServiceGraft` z metodami `place_order()` i `get_order()`.
W `__init__` woła `load_settings()` → `create_order_service(settings)`.
Zwraca JSON string — analogicznie do `PricingServiceGraft`.

### `order_service/graft/pyproject.toml`

Metadata wymagana przez gg (name, version, requires-python).

### `order_service/graft/Dockerfile`

- instaluje gg
- `pip install graft-pypi-pricing-service-graft` z custom registry
- `CMD ["gg", "--modules", "./order_service/graft/"]`

Brak symlinka — remote mode używa WebSocket, nie inmemory.

---

## Co zmieniamy

### `pricing_service/Dockerfile` → `pricing_service/graft/Dockerfile`

Przeniesienie dla spójności — każdy serwis trzyma Dockerfile przy module graft.

### `docker-compose.yml`

```yaml
pricing-graft:
  dockerfile: pricing_service/graft/Dockerfile
  ports: 80:80, 81:81          # Vision Pricing na localhost:81

order-graft:
  dockerfile: order_service/graft/Dockerfile
  ports: 82:80, 83:81          # Vision Order na localhost:83
  environment:
    PRICING_MODE: remote
    GRAFT_HOST: ws://pricing-graft/ws
  depends_on:
    - pricing-graft
```

### `Makefile`

- `run` → `docker compose up` (oba kontenery)
- `setup-local` zostaje bez zmian (lokalny dev poza Dockerem)

### `README.md`

Nowy opis flow, instrukcja dla obu Vision UI.

---

## Co zostaje bez zmian

- `order_service/services/`, `domain/`, `contracts/`, `ports/`
- `order_service/adapters/graft_pricing_provider.py`
- `order_service/config/settings.py`
- `order_service/bootstrap/factory.py`
- `order_service/tests/test_order_service*.py`, `test_factory.py`, `test_settings.py`, `test_graft_provider.py`
- `pricing_service/` — bez zmian
- Milestone 7 (`make setup-local`, symlink) — nadal działa dla lokalnego dev

---

## Flow po zmianach

### Remote (Docker)

```
docker compose up

pricing-graft (porty 80/81)
  └── PricingServiceGraft → PricingService
  └── Vision: localhost:81

order-graft (porty 82/83)
  └── OrderServiceGraft
      └── GraftPricingProvider(host=ws://pricing-graft/ws)
          └── WebSocket → pricing-graft:80
  └── Vision: localhost:83  ← tu testujesz place_order
```

### Local dev (poza Dockerem, bez zmian vs M7)

```
make setup-local
PRICING_MODE=local gg --modules ./order_service/graft/

Vision: localhost:81
  └── OrderServiceGraft
      └── GraftPricingProvider(host=None) → inmemory → symlink → PricingService
```

---

## Odkładamy na później

- Symlink w `order_service/graft/Dockerfile` dla `PRICING_MODE=local` w Dockerze

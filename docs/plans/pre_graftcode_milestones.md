# Plan: Doprowadzenie rozwiązania do stanu feature-complete (przed integracją GraftCode)

## Kontekst

Zadanie rekrutacyjne: dwie usługi Python (Pricing + Order) połączone przez GraftCode.
Baza kodu ma czystą architekturę port/adapter — integracja GraftCode to **wyłącznie**
zastąpienie stuba w `RemotePricingProvider` wygenerowanym Graftem.

**Cel planu:** kompletne rozwiązanie we wszystkich wymiarach *poza* GraftCode.

---

## Architektura — zasady nadrzędne

```
Zewnętrzny klient (curl / Postman / Vision)
      │ HTTP REST
      ▼
 Order Service API (FastAPI)        ← jedyny REST w systemie, nie zmienia się
      │
      ▼
 OrderService (Python class)
      │ LOCAL:  LocalPricingProvider → PricingService (in-process, czysty Python)
      │ REMOTE: RemotePricingProvider → GraftCode Graft → Gateway → PricingService
      ▼
 PricingService
   (bez HTTP, bez GraftCode w LOCAL mode)
```

**Kluczowe zasady:**
1. `PricingService` NIE MA i nigdy nie będzie miał HTTP endpointów
2. `OrderService`, `PricingProvider` Protocol, `LocalPricingProvider` — **bez zmian** dla GraftCode
3. Tylko `RemotePricingProvider` jest podmieniony przy przejściu na GraftCode
4. LOCAL mode = czysty Python, zero GraftCode, zero `gg`

---

## Co już jest dobre

- `PricingProvider` Protocol (port) + `LocalPricingProvider` / `RemotePricingProvider` ✅
- `Decimal` do obliczeń pieniężnych ✅
- `PricingRulesEngine` z Protocol-based regułami ✅
- Factory + DI przez konstruktor ✅
- Hierarchie wyjątków w obu usługach ✅
- Testy jednostkowe i integracyjne ✅

---

## Analiza luk

### Domena / logika biznesowa

| Problem | Lokalizacja | Priorytet |
|---------|-------------|-----------|
| `CustomerType(customer_type)` rzuca surowy `ValueError` dla nieznanych typów | `local_pricing_provider.py:29` | Wysoki |
| `OrderService` łapie tylko `PricingServiceUnavailableError`; `ProductNotFoundError` / `InvalidQuantityError` wyciekają z domeny pricing | `order_service.py:40` | Średni |
| Brak repozytorium zamówień — złożone zamówienia są tracone | `order_service.py` | Średni |
| Brak strukturalnego logowania | obie usługi | Niski |

### Infrastruktura

| Problem | Priorytet |
|---------|-----------|
| Brak HTTP API na Order Service — nie można testować zewnętrznie ani uruchomić w Dockerze | Wysoki |
| Brak konfiguracji przez zmienne środowiskowe (`PRICING_MODE` itp.) | Wysoki |
| `main.py` to zaślepka | Wysoki |
| Brak Dockerfile / Docker Compose / Makefile | Średni |
| `.DS_Store` nie jest w `.gitignore` | Niski |

### Dokumentacja

| Problem | Priorytet |
|---------|-----------|
| `README.md` jest pusty | Wysoki |

---

## Milestone 1 — Kompletność domeny i logiki biznesowej

**Pliki do zmiany / utworzenia:**

- `pricing_service/domain/exceptions.py` — dodanie `UnsupportedCustomerTypeError`
- `order_service/domain/exceptions.py` — dodanie `InvalidOrderRequestError`, `OrderNotFoundError`
- `order_service/adapters/local_pricing_provider.py` — przechwycenie `ValueError`
  z `CustomerType(...)` → `UnsupportedCustomerTypeError`
- `order_service/services/order_service.py`:
  - przechwycenie `ProductNotFoundError` / `InvalidQuantityError` /
    `UnsupportedCustomerTypeError` z providera → `InvalidOrderRequestError`
  - dodanie `dict[str, Order]` jako repozytorium in-memory
  - dodanie `get_order(order_id: str) -> OrderResult` — rzuca `OrderNotFoundError`
- `logger.info/debug/warning` w `PricingService.calculate_price`
  i `OrderService.place_order`
- Testy: pokrycie `InvalidOrderRequestError`, `OrderNotFoundError`, `get_order`;
  usunięcie duplikatu `test_order_failure.py` (pokryty przez `test_remote_mode.py`)

---

## Milestone 2 — Konfiguracja

**Pliki do zmiany / utworzenia:**

- `order_service/config/settings.py` — odczyt z `os.environ`:
  - `PRICING_MODE` (domyślnie `local`)
  - `GRAFTCODE_PROJECT_KEY` (zaślepka — wymagane w trybie remote)
- `order_service/bootstrap/factory.py` — automatyczny odczyt trybu z settings
- `main.py` — działający demo script: załaduj config → utwórz `OrderService` →
  złóż kilka zamówień (różne scenariusze) → wypisz wyniki
- `.env.example` — wszystkie zmienne z opisami i domyślami
- `.gitignore` — dodanie `.DS_Store`, `.env`, `.claude/`

---

## Milestone 3 — HTTP API na Order Service

**Cel:** Order Service uruchamialny jako serwer HTTP. Pricing Service bez zmian —
nadal czysty Python, zero HTTP.

**Uzasadnienie:** Docker wymaga wystawionego portu; klient zewnętrzny potrzebuje
punktu wejścia. W REMOTE mode GraftCode Vision będzie wywoływał ten sam API.
REST jest od klienta *do* Order Service, nie między serwisami — zgodne z zadaniem.

**Zależności do dodania w `pyproject.toml`:**
```toml
fastapi>=0.115
uvicorn[standard]>=0.34
```

**Nowe pliki — `order_service/api/`:**

- `app.py` — FastAPI app + lifespan (tworzy `OrderService` z settings)
- `routers/orders.py`:
  - `POST /orders` → `place_order`
  - `GET /orders/{order_id}` → `get_order`
- `schemas.py` — Pydantic `PlaceOrderRequest` / `OrderResponse`
- `error_handlers.py` — mapowanie wyjątków na HTTP:
  - `InvalidOrderRequestError` → 422
  - `OrderNotFoundError` → 404
  - `OrderPlacementError` → 503
- `order_service/__main__.py` — `uvicorn.run` jako punkt wejścia modułu

**Testy:**
- `order_service/tests/test_api.py` — testy przez `TestClient` FastAPI

---

## Milestone 4 — Docker, Docker Compose i Makefile

### Lokalizacja Dockerfiles

```
order_service/Dockerfile    ← ten sam obraz w obu trybach
pricing_service/Dockerfile  ← tylko w REMOTE mode (instaluje gg)
```

### LOCAL mode — jeden kontener (symulacja modularnego monolitu)

Order Service z Pricing uruchomionym in-process. Bez osobnego kontenera Pricing.
Nazwa usługi `order` pozostaje taka sama — to ta sama aplikacja, inna konfiguracja.

```yaml
# docker-compose.yml
services:
  order:
    build:
      context: .
      dockerfile: order_service/Dockerfile
    ports:
      - "8000:8000"
    environment:
      PRICING_MODE: local
    # LOCAL = modularny monolit — Pricing działa in-process
```

### REMOTE mode — dwa kontenery (po integracji GraftCode)

Pricing Service uruchamia `gg` (GraftCode Gateway) i rejestruje metody.
Order Service używa Graftu do komunikacji. Ten sam obraz `order`, inna konfiguracja.

```yaml
# docker-compose.remote.yml (override)
services:
  pricing:
    build:
      context: .
      dockerfile: pricing_service/Dockerfile
    ports:
      - "9080:80"   # wywołania GraftCode
      - "9081:81"   # Vision dla Pricing Service
    environment:
      GRAFTCODE_PROJECT_KEY: ${GRAFTCODE_PROJECT_KEY}

  order:
    environment:
      PRICING_MODE: remote
      GRAFTCODE_PROJECT_KEY: ${GRAFTCODE_PROJECT_KEY}
    depends_on:
      - pricing
```

**`pricing_service/Dockerfile`** (instaluje `gg` — tylko dla REMOTE mode):
```dockerfile
FROM python:3.13-bookworm
WORKDIR /usr/app
COPY ./pricing_service /usr/app/pricing-service/
COPY ./pyproject.toml /usr/app/pricing-service/
RUN apt-get update \
 && apt-get install -y wget \
 && wget -O /usr/app/gg.deb \
      https://github.com/grft-dev/graftcode-gateway/releases/latest/download/gg_linux_amd64.deb \
 && dpkg -i /usr/app/gg.deb && rm /usr/app/gg.deb \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
EXPOSE 80
EXPOSE 81
CMD ["gg", "--modules", "./pricing-service/"]
```

**`order_service/Dockerfile`** (identyczny w LOCAL i REMOTE — różnica tylko w env):
```dockerfile
FROM python:3.13-slim
WORKDIR /usr/app
COPY . /usr/app/
RUN pip install uv && uv sync
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "order_service"]
```

### Makefile

```makefile
.PHONY: test demo run-local run-remote

test:
	uv run pytest -q

demo:
	uv run python main.py

run-local:
	docker compose up --build

run-remote:
	docker compose -f docker-compose.yml -f docker-compose.remote.yml up --build
```

---

## Milestone 5 — README i dokumentacja

**Sekcje:**
1. Quick start (`make run-local`, `make demo`, `make test`)
2. Jak testować (pytest, `curl` / Postman pod `:8000/orders`)
3. Architektura: diagram LOCAL vs REMOTE, dlaczego NIE REST między serwisami
4. Jak działa GraftCode i co trzeba zrobić, żeby REMOTE mode zadziałał
5. Reguły cenowe: strategia + silnik reguł — decyzja projektowa
6. Edge cases: Decimal, zaokrąglanie, ilość 0, nieznany typ klienta
7. Obsługa błędów: retry, timeout, taksonomia wyjątków
8. Wersjonowanie / kompatybilność wsteczna

---

## Milestone 6 — Integracja GraftCode (poza zakresem teraz)

**Dwie zmiany w kodzie:**

1. `order_service/adapters/remote_pricing_provider.py` — zamiana stuba:
```python
# PRZED:
#   raise ConnectionError()

# PO:
from graft_pypi_pricingservice import PricingService as PricingGraft
graft = PricingGraft()
result = await graft.calculate_price(product_id, quantity, customer_type)
return PricingQuote(...)
```

2. `Dockerfile.order` w REMOTE mode — instalacja wygenerowanego Graftu:
```dockerfile
RUN pip install <wygenerowany-graft-package>
```

`OrderService`, `PricingProvider` Protocol, API, logika biznesowa — **bez zmian**.

---

## Weryfikacja

**Po Milestone 1–2:**
```bash
make test
make demo
```

**Po Milestone 3:**
```bash
PRICING_MODE=local uv run python -m order_service
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'
```

**Po Milestone 4:**
```bash
make run-local
curl -X POST http://localhost:8000/orders ...
```
# Plan: Revised Milestones 4, 5, 6

## Context

Oryginalna architektura miała:
- `LocalPricingProvider` → bezpośrednie wywołanie `PricingService` (in-process)
- `RemotePricingProvider` → stub rzucający `ConnectionError`
- `OrderService` importujący wyjątki z `pricing_service.domain.exceptions` (naruszenie granic serwisów)
- Milestone 6 (GraftCode) oznaczony jako "out of scope"

Po zainstalowaniu wygenerowanego klienta Graft:
- **Remote mode działa**: `GraftConfig.host = "ws://localhost/ws"` + `PricingServiceGraft()`
- **Local mode (in-memory)** nie działa — bug Graft alpha
- Graft integration wchodzi do zakresu — stary Milestone 6 zostaje wchłonięty przez nowy Milestone 4

Milestony zostają przeorganizowane:

| # | Nazwa | Status |
|---|-------|--------|
| 1 | Domain & business logic | ✅ done |
| 2 | Configuration | ✅ done |
| 3 | HTTP API (FastAPI) | ✅ done |
| **4** | **GraftCode integration (architecture refactor)** | pending |
| **5** | **Docker, Docker Compose, Makefile** | pending |
| **6** | **README & documentation** | pending |

---

## Instalacja paczki Graft

```bash
uv pip install \
  --extra-index-url https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free \
  graft-pypi-graftcode-homework==0.1.0
```

Import po stronie klienta (order service):
```python
from graft_pypi_graftcode_homework.pricingservicegraft import PricingServiceGraft
from graft_pypi_graftcode_homework.graft.pypi.graftcode_homework.graft_config import GraftConfig
```

---

## Docelowa architektura

```
OrderService (zna tylko order_service.*)
     │
     ▼
PricingProvider (protocol, order_service/ports/)
     │
     ▼
GraftPricingProvider (adapter, order_service/adapters/)
     │
     ▼
PricingServiceGraft (klient wygenerowany — graft_pypi_graftcode_homework)
     │ REMOTE: GraftConfig.host = settings.graft_host
     │ LOCAL:  GraftConfig.host nie ustawiony (bug Graft — nie działa)
     ▼
gg Gateway → PricingServiceGraft (server-side, pricing_service/graft/)
```

**Kluczowe zasady:**
- `order_service` ma ZERO importów z `pricing_service.*`
- `GraftPricingProvider` tłumaczy błędy Graft na `order_service.domain.exceptions`
- `PricingProvider` protokół pozostaje — umożliwia fake'i w testach

---

## Milestone 4: GraftCode integration (architecture refactor)

### Krok 1: Zbadaj wyjątki Graft (przed napisaniem adaptera)

Uruchom skrypt z działającym lokalnie `gg` i serwisem Pricing:

```python
from graft_pypi_graftcode_homework.pricingservicegraft import PricingServiceGraft
from graft_pypi_graftcode_homework.graft.pypi.graftcode_homework.graft_config import GraftConfig

GraftConfig.host = "ws://localhost/ws"
service = PricingServiceGraft()

for label, args in [
    ("nieznany produkt", ("unknown_product", 1, "regular")),
    ("quantity=0",       ("laptop", 0, "regular")),
    ("nieznany customer",("laptop", 1, "vip")),
]:
    try:
        print(label, "→", service.calculate_price(*args))
    except Exception as e:
        print(label, f"→ {type(e).__module__}.{type(e).__name__}: {e}")
```

Na podstawie wyników ustalić w adapterze:
- Czy graft re-rzuca oryginalne wyjątki z `pricing_service.domain.exceptions` → mapować po typie
- Czy rzuca własne typy (np. `GraftError`, `GraftCallError`) → mapować po klasie lub treści wiadomości
- Czy błędy domenowe wracają jako poprawna odpowiedź JSON z polem `error` → parsować response

---

### Krok 2: Usuń `pricing_service.*` z `order_service`

**Pliki do usunięcia:**
- `order_service/adapters/local_pricing_provider.py`
- `order_service/adapters/remote_pricing_provider.py`

**Zmień: `order_service/services/order_service.py`**

Usuń import:
```python
from pricing_service.domain.exceptions import (
    ProductNotFoundError,
    InvalidQuantityError,
    UnsupportedCustomerTypeError,
)
```

Uproszczona logika catch — błędy domenowe tłumaczy adapter, `OrderService` nie musi znać typów z pricing:
```python
try:
    quote = self._pricing_provider.calculate_price(...)
except PricingServiceUnavailableError as exc:
    raise OrderPlacementError("Unable to place order because pricing service is unavailable.") from exc
# InvalidOrderRequestError propaguje naturalnie
```

---

### Krok 3: Nowy adapter `order_service/adapters/graft_pricing_provider.py`

```python
import json
from decimal import Decimal

from graft_pypi_graftcode_homework.pricingservicegraft import PricingServiceGraft
from order_service.contracts.pricing_quote import PricingQuote
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    PricingServiceUnavailableError,
)
from order_service.ports.pricing_provider import PricingProvider


class GraftPricingProvider(PricingProvider):

    def __init__(self):
        self._client = PricingServiceGraft()

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:
        try:
            result_json = self._client.calculate_price(product_id, quantity, customer_type)
            result = json.loads(result_json)
            return PricingQuote(
                product_id=result["product_id"],
                unit_price=Decimal(result["unit_price"]),
                quantity=result["quantity"],
                discount_percent=Decimal(result["discount_percent"]),
                total_price=Decimal(result["total_price"]),
            )
        except <DomainValidationException> as exc:   # ← uzupełnić po Kroku 1
            raise InvalidOrderRequestError(str(exc)) from exc
        except Exception as exc:
            raise PricingServiceUnavailableError("Pricing service unavailable.") from exc
```

> Schemat `except` wypełnić po zbadaniu wyjątków Graft.

---

### Krok 4: `pyproject.toml` — dodaj paczkę i custom index

```toml
[project]
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "graft-pypi-graftcode-homework==0.1.0",
]

[[tool.uv.index]]
name = "graftcode"
url = "https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free"

[tool.uv.sources]
graft-pypi-graftcode-homework = { index = "graftcode" }
```

### Krok 5: `settings.py` i `factory.py`

**`order_service/config/settings.py`:**
- Usuń `graftcode_project_key` (należy do gg binary po stronie Pricing, nie Order Service)
- Dodaj `graft_host: str | None`; odczytaj z `GRAFT_HOST` env var; wymagany gdy `PRICING_MODE=remote`

```python
@dataclass(frozen=True)
class Settings:
    pricing_mode: PricingMode
    graft_host: str | None
```

**`order_service/bootstrap/factory.py`:**

```python
from graft_pypi_graftcode_homework.graft.pypi.graftcode_homework.graft_config import GraftConfig
from order_service.adapters.graft_pricing_provider import GraftPricingProvider

def create_order_service_from_settings(settings: Settings) -> OrderService:
    if settings.pricing_mode == PricingMode.REMOTE:
        GraftConfig.host = settings.graft_host
    return OrderService(pricing_provider=GraftPricingProvider())
```

Usuń `create_order_service(mode)`.

### Krok 6: Testy

**Usuń:**
- `test_remote_mode.py` (testuje stub, zawsze ConnectionError)
- `test_local_provider.py`
- `tests/integration/` (używają LocalPricingProvider)

**Zaktualizuj:**
- `test_factory.py` — patch `GraftConfig` i `GraftPricingProvider`
- `test_settings.py` — usuń asercje `GRAFTCODE_PROJECT_KEY`, dodaj `GRAFT_HOST`

**Nowy:**
- `test_graft_provider.py` — mockuje `PricingServiceGraft`; pokrywa:
  - mapowanie JSON → PricingQuote (Decimal z string)
  - mapowanie wyjątków → `InvalidOrderRequestError` / `PricingServiceUnavailableError`

**Bez zmian:**
- `test_api.py`, `test_order_service.py`, `test_order_service_domain_errors.py`,
  `test_order_service_extended.py`, `fakes/`

---

## Milestone 5: Docker, Docker Compose, Makefile

### `docker-compose.yml` (zastąp obecny)

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

> `ws://pricing-graft/ws` — Docker internal DNS, port 80 gg gateway. Do weryfikacji przy `make run`.

### `pricing_service/Dockerfile` — popraw CMD

Obecna linia nie przekazuje project key — fix:
```dockerfile
CMD ["sh", "-c", "gg --projectKey \"$GRAFTCODE_PROJECT_KEY\" --modules ./pricing_service/graft/"]
```

### `order_service/Dockerfile` — nowy plik

```dockerfile
FROM python:3.13-slim
WORKDIR /usr/app
COPY . /usr/app/
RUN pip install uv && uv sync --no-dev
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "order_service"]
```

> `uv sync --no-dev` korzysta z `[[tool.uv.index]]` skonfigurowanego w `pyproject.toml`,
> więc custom registry Graft jest dostępny bez dodatkowych flag.

### `.env.example` — nowy plik

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

---

## Milestone 6: README & documentation

Sekcje:

1. **Quick start** — `make run`, wymagania (Docker, konto GraftCode, `.env`)
2. **Setup** — gdzie wziąć i jak ustawić `GRAFTCODE_PROJECT_KEY`
3. **Architektura** — diagram `OrderService → PricingProvider → GraftPricingProvider → gg → PricingService`;
   dlaczego Graft zamiast REST między serwisami
4. **Konfiguracja** — env vars: `PRICING_MODE`, `GRAFT_HOST`
5. **Reguły cenowe** — strategy pattern, `PricingRulesEngine`, konfigurowalność, max discount cap 20%
6. **Edge cases** — Decimal vs float, zaokrąglanie, quantity 0, nieznany customer type, brak produktu
7. **Obsługa błędów** — taksonomia wyjątków, granica serwisów (order nie zna pricing exceptions)
8. **Testowanie** — `make test`, curl, Vision UI pod `:81`
9. **Known limitations**:
   - Local mode (in-memory Graft) nie działa — bug Graft alpha; do weryfikacji po poprawce Graft
   - Błędy domenowe przez Graft — zachowanie opisane po zbadaniu (Milestone 4, Krok 1)
10. **Wersjonowanie / backward compatibility** — jak podchodzić do zmian sygnatur metod w Graft

---

## Known limitations do udokumentowania

| Limitation | Wpływ |
|---|---|
| Local mode (in-memory Graft) nie działa | Tylko remote mode możliwy; `PRICING_MODE=local` nie ma zastosowania w Docker |
| Graft exception propagation — zbadane w M4/Krok 1 | Error handling doprecyzowany po teście |

---

## Weryfikacja (end-to-end po Milestone 5)

```bash
# Testy jednostkowe
make test

# Uruchomienie z Docker Compose
cp .env.example .env  # wypełnij GRAFTCODE_PROJECT_KEY
make run

# Test endpoint
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "premium"}'

# Vision UI
open http://localhost:81
```

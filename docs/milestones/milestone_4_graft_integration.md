# Milestone 4 — GraftCode Integration (Architecture Refactor)

## Status: pending

## Scope

Zastąpienie wzorca Local/Remote provider jednym `GraftPricingProvider` opartym
na wygenerowanym kliencie Graft. Usunięcie wszelkich importów `pricing_service.*`
z `order_service`.

### Pliki do usunięcia
- `order_service/adapters/local_pricing_provider.py`
- `order_service/adapters/remote_pricing_provider.py`
- `order_service/tests/test_remote_mode.py`
- `order_service/tests/test_local_provider.py`
- `order_service/tests/integration/` (cały katalog)

### Pliki do utworzenia
- `order_service/adapters/graft_pricing_provider.py`
- `order_service/tests/test_graft_provider.py`

### Pliki do zmiany
- `order_service/services/order_service.py` — usuń import z `pricing_service.domain.exceptions`
- `order_service/bootstrap/factory.py` — zastąp LocalPricingProvider/RemotePricingProvider przez GraftPricingProvider + GraftConfig
- `order_service/config/settings.py` — usuń `graftcode_project_key`, dodaj `graft_host`
- `order_service/tests/test_factory.py` — patch GraftConfig i GraftPricingProvider
- `order_service/tests/test_settings.py` — usuń asercje GRAFTCODE_PROJECT_KEY, dodaj GRAFT_HOST
- `pyproject.toml` — dodaj `graft-pypi-graftcode-homework==0.1.0` + custom index

## Kroki implementacji

### Krok 1: Zbadaj wyjątki Graft

Przed napisaniem adaptera uruchom skrypt diagnostyczny (z działającym `gg`):

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

Na podstawie wyników doprecyzować bloki `except` w adapterze.

### Krok 2: GraftPricingProvider

```python
class GraftPricingProvider(PricingProvider):
    def __init__(self):
        self._client = PricingServiceGraft()

    def calculate_price(self, product_id, quantity, customer_type) -> PricingQuote:
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
        except <DomainError> as exc:          # ← ustalić po Kroku 1
            raise InvalidOrderRequestError(str(exc)) from exc
        except Exception as exc:
            raise PricingServiceUnavailableError("Pricing service unavailable.") from exc
```

### Krok 3: OrderService — usuń pricing_service imports

```python
# Usuń:
from pricing_service.domain.exceptions import (
    ProductNotFoundError, InvalidQuantityError, UnsupportedCustomerTypeError,
)

# Uproszczony catch — adapter już tłumaczy:
try:
    quote = self._pricing_provider.calculate_price(...)
except PricingServiceUnavailableError as exc:
    raise OrderPlacementError("...") from exc
# InvalidOrderRequestError propaguje naturalnie
```

### Krok 4: pyproject.toml

```toml
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

Instalacja lokalna:
```bash
uv pip install \
  --extra-index-url https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free \
  graft-pypi-graftcode-homework==0.1.0
```

### Krok 5: settings.py i factory.py

`settings.py`: usuń `graftcode_project_key`, dodaj `graft_host: str | None` z env var `GRAFT_HOST`.

`factory.py`:
```python
def create_order_service_from_settings(settings: Settings) -> OrderService:
    if settings.pricing_mode == PricingMode.REMOTE:
        GraftConfig.host = settings.graft_host
    return OrderService(pricing_provider=GraftPricingProvider())
```

Usuń `create_order_service(mode)`.

## Docelowa architektura

```
OrderService (zna tylko order_service.*)
     │
PricingProvider (protocol)
     │
GraftPricingProvider (adapter)
     │
PricingServiceGraft (klient — graft_pypi_graftcode_homework)
     │ REMOTE: GraftConfig.host = settings.graft_host
     │ LOCAL:  bez hosta (in-memory; bug Graft alpha — nie działa)
     ▼
gg Gateway → PricingServiceGraft (server-side)
```

## Known limitations

- **Local mode** (in-memory Graft) nie działa — bug Graft alpha
- **Wyjątki domenowe przez Graft** — zachowanie określone po Kroku 1; do momentu weryfikacji
  wszystkie błędy klienta trafiają do `PricingServiceUnavailableError`

## Details

See: `docs/plans/milestone_4_5_6_revised_plan.md` → Milestone 4.

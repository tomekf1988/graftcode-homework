# Plan: Milestone 7 — GraftCode local (inmemory) mode

## Cel

Umożliwić przełączanie między:
- `PRICING_MODE=remote` — graft przez WebSocket do `gg` w Dockerze (status quo)
- `PRICING_MODE=local`  — graft inmemory, bez Dockera, bez sieci

## Kontekst techniczny

`GraftConfig.host` domyślnie to `"inmemory"`. W tym trybie graft ładuje moduł
z lokalnego katalogu, zamiast łączyć się przez WebSocket.

Graft szuka modułu w:
```
site-packages/graft_pypi_pricing_service_graft/graft.pricing_service_graft/
```
Ten katalog nie istnieje po standardowym `make setup`.

`pricing_service_graft.py` importuje `pricing_service.*` — pakiet ten nie jest
zainstalowany w venvie order_service.

## Rozwiązanie

### 1. Moduł graft

Skopiować do katalogu modułu dwa pliki ze źródła:
- `pricing_service/graft/pricing_service_graft.py`
- `pricing_service/graft/pyproject.toml`

### 2. Dostępność `pricing_service`

Symlink w `site-packages/`:
```
site-packages/pricing_service  →  $(CURDIR)/pricing_service
```
Python przy imporcie szuka w `site-packages/` — symlink sprawia, że
`import pricing_service` działa bez kopiowania plików i bez `.pth`.

### 3. Przełącznik `PRICING_MODE`

`Settings` dostaje pole `pricing_mode`. Factory przekazuje `host` do
`GraftPricingProvider` tylko gdy `pricing_mode == "remote"`.
Gdy `pricing_mode == "local"` — `host=None`, `GraftConfig.host` zostaje
domyślnym `"inmemory"`.

---

## Zmiany w kodzie

### `order_service/config/settings.py`
```python
@dataclass(frozen=True)
class Settings:
    pricing_mode: str        # "remote" | "local"
    graft_host: str | None   # używane tylko gdy pricing_mode == "remote"

def load_settings() -> Settings:
    return Settings(
        pricing_mode=os.environ.get("PRICING_MODE", "remote").lower(),
        graft_host=os.environ.get("GRAFT_HOST"),
    )
```

### `order_service/bootstrap/factory.py`
```python
def create_order_service(settings: Settings) -> OrderService:
    host = settings.graft_host if settings.pricing_mode == "remote" else None
    return OrderService(pricing_provider=GraftPricingProvider(host=host))
```

### `Makefile`

Symlink trafia do `graft_pypi_pricing_service_graft/` — jako sibling katalogu modułu.
Odzwierciedla układ z Dockera: moduł i pakiet `pricing_service` są w tym samym katalogu
nadrzędnym (w Dockerze to `/usr/app`, lokalnie to `graft_pypi_pricing_service_graft/`).

```makefile
PYTHON_VERSION   := 3.13
SITE_PACKAGES    := order_service/.venv/lib/python$(PYTHON_VERSION)/site-packages
GRAFT_PKG_DIR    := $(SITE_PACKAGES)/graft_pypi_pricing_service_graft
GRAFT_MODULE_DIR := $(GRAFT_PKG_DIR)/graft.pricing_service_graft

setup:
    uv sync --directory order_service
    cd order_service && uv pip install graft-pypi-pricing-service-graft==0.1.0

setup-local: setup
    mkdir -p $(GRAFT_MODULE_DIR)
    cp pricing_service/graft/pricing_service_graft.py $(GRAFT_MODULE_DIR)/
    cp pricing_service/graft/pyproject.toml $(GRAFT_MODULE_DIR)/
    ln -sfn $(CURDIR)/pricing_service $(GRAFT_PKG_DIR)/pricing_service
```

### `.env`
```
PRICING_MODE=remote          # remote | local
GRAFT_HOST=ws://localhost/ws  # używane tylko gdy PRICING_MODE=remote
```

---

## Testy

- `test_settings.py` — `PRICING_MODE=local` parsuje poprawnie, `host` ignorowany
- `test_factory.py` — `pricing_mode=local` → `GraftPricingProvider(host=None)`
- ręczne `make setup-local` + `PRICING_MODE=local make run` → `POST /orders` działa

---

## Weryfikacja end-to-end

```bash
make setup-local
# w .env: PRICING_MODE=local (usuń lub zignoruj GRAFT_HOST)
uv run --project order_service python -m order_service

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "laptop", "quantity": 2, "customer_type": "regular"}'
# oczekiwane: {"order_id": "...", "total_price": "10000", ...}
```

Brak Dockera, brak sieci — pricing działa in-process przez graft inmemory.

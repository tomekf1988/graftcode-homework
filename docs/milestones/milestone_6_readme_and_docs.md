# Milestone 6 — README & Documentation

## Status: pending

## Scope

Kompletny `README.md` spełniający wymagania zadania rekrutacyjnego.

## Sekcje README

1. **Quick start**
   - `make run` — uruchomienie całości przez Docker Compose
   - `make test` — testy jednostkowe
   - Wymagania: Docker, konto GraftCode, plik `.env`

2. **Setup**
   - Skąd wziąć `GRAFTCODE_PROJECT_KEY` (portal.graftcode.com)
   - Jak skonfigurować `.env`

3. **Architektura**
   - Diagram:
     ```
     Klient HTTP
       │ POST /orders
       ▼
     Order Service (FastAPI, :8000)
       │ PricingProvider protocol
       ▼
     GraftPricingProvider
       │ WebSocket (GRAFT_HOST)
       ▼
     gg Gateway (:80)
       │
       ▼
     PricingServiceGraft (server-side)
       │
       ▼
     PricingService (logika domenowa)
     ```
   - Dlaczego Graft zamiast REST między serwisami
   - LOCAL vs REMOTE mode — przełączanie przez konfigurację, bez zmian w logice

4. **Konfiguracja**
   - `PRICING_MODE` (local / remote)
   - `GRAFT_HOST` (wymagane gdy remote, domyślnie `ws://localhost/ws`)
   - `GRAFTCODE_PROJECT_KEY` (po stronie Pricing / gg)

5. **Reguły cenowe**
   - Strategy pattern: `PricingRule` Protocol + `PricingRulesEngine`
   - Reguły: `PremiumCustomerRule` (10%), `BulkOrderRule` (5% gdy qty≥10), cap 20%
   - Dodawanie nowych reguł bez zmiany silnika

6. **Edge cases**
   - `Decimal` zamiast `float` — precyzja finansowa
   - Zaokrąglanie: brak — `Decimal` bez `round()`
   - `quantity=0` → `InvalidQuantityError` → HTTP 400
   - Nieznany customer type → `UnsupportedCustomerTypeError` → HTTP 400
   - Nieznany produkt → `ProductNotFoundError` → HTTP 400

7. **Obsługa błędów**
   - Taksonomia: `InvalidOrderRequestError` (400) / `OrderPlacementError` (503)
   - `order_service` nie zna typów z `pricing_service` — granica serwisów respektowana
   - `PricingServiceUnavailableError` → HTTP 503

8. **Testowanie**
   - `make test` — pytest
   - `curl` — przykłady dla happy path i błędów
   - Vision UI pod `:81` — testowanie Pricing Service przez interfejs Graft

9. **Known limitations**
   - Local mode (in-memory Graft) nie działa — bug Graft alpha
   - Błędy domenowe przez Graft w remote mode: zachowanie opisane po weryfikacji (M4)

10. **Wersjonowanie / backward compatibility**
    - Jak podchodzić do zmian sygnatur metod w Graft
    - Dodawanie pól: nowe pola opcjonalne nie łamią kompatybilności
    - Zmiana sygnatur: nowa metoda obok starej; stara deprecatowana

## Details

See: `docs/plans/milestone_4_5_6_revised_plan.md` → Milestone 6.

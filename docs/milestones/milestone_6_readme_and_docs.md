# Milestone 6 — README & Documentation

## Status: pending

## Scope

A complete `README.md` fulfilling the requirements of the recruitment task.

## README sections

1. **Quick start**
   - `make run` — start everything via Docker Compose
   - `make test` — run unit tests
   - Prerequisites: Docker, GraftCode account, `.env` file

2. **Setup**
   - Where to obtain `GRAFTCODE_PROJECT_KEY` (portal.graftcode.com)
   - How to configure `.env`

3. **Architecture**
   - Diagram:
     ```
     HTTP client
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
     PricingService (domain logic)
     ```
   - Why Graft instead of REST between services
   - LOCAL vs REMOTE mode — switched via config, no logic changes required

4. **Configuration**
   - `PRICING_MODE` (`local` / `remote`)
   - `GRAFT_HOST` (required in remote mode, defaults to `ws://localhost/ws`)
   - `GRAFTCODE_PROJECT_KEY` (Pricing Service / gg side only)

5. **Pricing rules**
   - Strategy pattern: `PricingRule` protocol + `PricingRulesEngine`
   - Rules: `PremiumCustomerRule` (10%), `BulkOrderRule` (5% when qty≥10), 20% cap
   - New rules can be added without modifying the engine

6. **Edge cases**
   - `Decimal` instead of `float` — financial precision
   - No rounding — `Decimal` arithmetic without `round()`
   - `quantity=0` → `InvalidQuantityError` → HTTP 400
   - Unknown customer type → `UnsupportedCustomerTypeError` → HTTP 400
   - Unknown product → `ProductNotFoundError` → HTTP 400

7. **Error handling**
   - Taxonomy: `InvalidOrderRequestError` (400) / `OrderPlacementError` (503)
   - `order_service` has no knowledge of `pricing_service` exception types — service boundary respected
   - `PricingServiceUnavailableError` → HTTP 503

8. **Testing**
   - `make test` — pytest
   - `curl` — examples for happy path and error cases
   - Vision UI at `:81` — test Pricing Service via the Graft UI

9. **Known limitations**
   - Local mode (in-memory Graft) does not work — bug in Graft alpha
   - Domain errors in remote mode: translated by `GraftPricingProvider` via `HypertubeException`

10. **Versioning / backward compatibility**
    - How to handle method signature changes in Graft
    - New optional fields do not break compatibility
    - Signature changes: add new method alongside old; deprecate old

## See also

`docs/plans/milestone_4_5_6_revised_plan.md` → Milestone 6.

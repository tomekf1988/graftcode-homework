# Review: Milestone 4 — GraftCode Integration

## Summary

The milestone successfully isolates `order_service` from `pricing_service` at the import level. The new `GraftPricingProvider` adapter is clean and focused. Exception mapping is reasonable for the SDK version in use. Test coverage is solid for the adapter unit tests and API integration tests. Three issues are worth addressing: a dead exception handler registration in `app.py`, a `GraftConfig` mutation that creates test-isolation risk, and the validation ordering in `pricing_service` that gives misleading errors.

---

## Critical issues

### 1. `PricingServiceUnavailableError` has a registered handler but is never raised to the API layer

`app.py` registers a handler for `PricingServiceUnavailableError` (line 35), but `OrderService.place_order` catches that exception and re-raises it as `OrderPlacementError` before it ever reaches FastAPI. The `PricingServiceUnavailableError` handler at the app level is therefore unreachable dead code.

The result is that both `PricingServiceUnavailableError` and `OrderPlacementError` map to 503 (the right status), but only by accident — whichever handler fires depends on which exception escapes. Right now `OrderPlacementError` always fires. The `PricingServiceUnavailableError` handler is never exercised, and its presence misleads readers about the actual exception flow.

Fix: either remove the `PricingServiceUnavailableError` handler from `app.py` (it is already caught and wrapped upstream), or document clearly why it is kept as a safety net.

### 2. `GraftConfig.host` is a class-level mutation — test isolation is not guaranteed

`GraftPricingProvider.__init__` writes `GraftConfig.host = host` at the class level. In the current tests this is patched away via `patch("...GraftConfig")`, so tests pass. However, any test that constructs a real `GraftPricingProvider` (or where the patch is incomplete) will mutate global class state that persists across tests within the same process. This is especially fragile if tests run in parallel or if future tests instantiate the provider without patching.

The patch in `_make_provider` patches the entire `GraftConfig` class rather than just the attribute assignment; that works but is more aggressive than needed and hides whether the assignment path is actually tested. A safer approach is to pass the host as a constructor argument and assign it inside `__init__`, keeping the global mutation contained to the explicit call site and making it trivially testable without patching.

---

## Suggested improvements

### 3. Validation order in `PricingService.calculate_price` produces misleading errors

`pricing_service/services/pricing_service.py` validates `customer_type` first, then `quantity`, then does the product lookup. This means a request with both an invalid product and zero quantity raises `UnsupportedCustomerTypeError` (or `InvalidQuantityError`) rather than surfacing the domain error the caller most likely cares about. Convention in most domain services is: validate the cheapest/most fundamental constraints first — quantity is cheapest — then check catalog membership, then validate enums. Reordering to `quantity → customer_type → product` is a minor change but produces more intuitive error messages.

### 4. `Settings.pricing_mode` is unused after M4

`create_order_service_from_settings` ignores `settings.pricing_mode` entirely and always creates a `GraftPricingProvider`. The `PricingMode` enum and the mode-parsing logic in `load_settings` are now dead code. This is noted in the architecture decisions as intentional, but it creates a gap: the setting is validated at startup (raising on invalid values) but has no effect. A comment in `factory.py` explaining that the mode is reserved for future use would prevent future maintainers from removing the factory's `settings` parameter as "unused".

### 5. `create_order_service_from_settings` parameter is vestigial

The factory signature accepts `settings: Settings` but never reads from it. Either use it (e.g., branch on `pricing_mode`) or drop the parameter to eliminate a misleading signature. If future branching is planned, a `# TODO` comment is sufficient justification to keep it.

### 6. `PricingServiceTimeoutError` in `exceptions.py` is defined but never raised or handled

`order_service/domain/exceptions.py` defines `PricingServiceTimeoutError`. Nothing in M4 raises it, handles it, or registers an HTTP handler for it. If it is not planned for a near-future milestone, remove it to keep the exception hierarchy honest.

### 7. JSON round-trip between `pricing_service` and `order_service` is fragile

`PricingServiceGraft.calculate_price` serialises `PriceCalculationResult` to JSON (`json.dumps(result.to_dict())`) and `GraftPricingProvider.calculate_price` immediately deserialises it (`json.loads(result_json)`). This round-trip exists because the Graft-generated boundary forces a string wire format. That is acceptable for an alpha SDK, but the `Decimal` fields are serialised via `str()` and parsed back with `Decimal(result["unit_price"])`. If the pricing service ever returns a value in scientific notation or with unexpected precision, the conversion will silently produce wrong numbers. Adding an explicit `Decimal`-safe path or at least a comment acknowledging the assumption would reduce future debugging time.

---

## Positive observations

- The service boundary is clean: zero `pricing_service.*` imports remain in `order_service` proper (only the adapter test file imports `HypertubeException`, which is correct).
- Exception mapping in `GraftPricingProvider` is minimal and explicit. The two-clause `try/except` (domain error vs. everything else) is easy to reason about.
- `GraftPricingProvider.__init__` reading `GRAFT_HOST` directly keeps graft-specific knowledge inside the adapter, consistent with the architecture decision.
- `FakePricingProvider` pattern keeps API tests fast and independent of the Graft SDK.
- `_make_provider` helper in `test_graft_provider.py` is clean; four focused test cases cover the critical paths (happy path, domain error, connection error, generic error).
- `OrderService` is notably simpler after M4 — no more cross-domain exception imports.

---

## Verdict

**LGTM with minor fixes**

The architecture refactor is solid and the core adapter is correct. Fix the dead `PricingServiceUnavailableError` handler registration to avoid future confusion (critical), and address the `GraftConfig` class-level mutation concern before adding parallelism or more adapter-level tests (critical). The remaining items are genuinely optional.

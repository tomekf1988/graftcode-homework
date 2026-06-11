# Milestone 1 — Domain & Business Logic Completeness

## Status: ✅ done

## What was implemented

- New exceptions: `UnsupportedCustomerTypeError`, `InvalidOrderRequestError`, `OrderNotFoundError`
- `LocalPricingProvider`: `CustomerType(...)` no longer leaks `ValueError` — raises `UnsupportedCustomerTypeError` instead
- `OrderService.place_order`: catches validation errors from the provider and wraps them in `InvalidOrderRequestError`
- `OrderService`: in-memory order store (`dict[str, Order]`) + `get_order` method
- Structured logging in `PricingService` and `OrderService`
- Removed duplicate `test_order_failure.py`
- 7 new tests (unit + integration)

## Architectural decisions

Recorded in CLAUDE.md under "Architecture decisions (Milestone 1)".

## Test results

```
20 passed in 0.24s
```

## Artifacts

- `docs/prs/milestone_1_domain_and_business_logic.md`
- `tasks/done.md`, `tasks/in_progress.md`, `tasks/todo.md`

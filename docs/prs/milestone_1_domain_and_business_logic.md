# Milestone 1 — Domain & Business Logic Completeness

## Summary

Closes all domain-level gaps identified in the pre-GraftCode plan:
proper exception hierarchy, validated customer type conversion, in-memory order store,
`get_order` retrieval, structured logging, and expanded test coverage.

## Changes

### New exceptions
- `pricing_service/domain/exceptions.py`: added `UnsupportedCustomerTypeError(PricingError)`
- `order_service/domain/exceptions.py`: added `InvalidOrderRequestError(OrderError)` and `OrderNotFoundError(OrderError)`

### LocalPricingProvider fix
- `order_service/adapters/local_pricing_provider.py`: `CustomerType(customer_type)` now catches
  `ValueError` and raises `UnsupportedCustomerTypeError` instead of leaking a bare `ValueError`

### OrderService improvements
- Catches `ProductNotFoundError`, `InvalidQuantityError`, `UnsupportedCustomerTypeError` from the
  pricing provider and re-raises as `InvalidOrderRequestError` — keeps order-domain clean from
  pricing-domain exception types
- Added `dict[str, Order]` in-memory store; each placed order is persisted there
- Added `get_order(order_id: str) -> OrderResult` — raises `OrderNotFoundError` for unknown IDs

### Structured logging
- `pricing_service/services/pricing_service.py`: `logger.info` at entry, `logger.debug` before return
- `order_service/services/order_service.py`: `logger.info` at entry and after order creation,
  `logger.warning` when catching validation errors

### Tests
- Deleted `test_order_failure.py` (duplicate of `test_remote_mode.py`)
- Updated `test_order_service_domain_errors.py`: now expects `InvalidOrderRequestError` (correct behavior)
- Updated `test_order_local_validation.py`: same correction for integration test
- Added `test_order_service_extended.py` (5 unit tests)
- Added `test_local_provider.py` (1 unit test for unknown customer type)
- Added `integration/test_order_get_local.py` (end-to-end: place then retrieve via LOCAL adapter)

## Test results

```
20 passed in 0.24s
```

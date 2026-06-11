# DONE — Milestone 1

- [x] Add `UnsupportedCustomerTypeError` to `pricing_service/domain/exceptions.py`
- [x] Add `InvalidOrderRequestError` and `OrderNotFoundError` to `order_service/domain/exceptions.py`
- [x] Fix `LocalPricingProvider`: catch `ValueError` from `CustomerType(...)` → raise `UnsupportedCustomerTypeError`
- [x] Fix `OrderService.place_order`: catch `ProductNotFoundError`, `InvalidQuantityError`, `UnsupportedCustomerTypeError` → wrap in `InvalidOrderRequestError`
- [x] Add in-memory order store (`dict[str, Order]`) to `OrderService`
- [x] Store each placed order in the dict after creation
- [x] Add `get_order(order_id: str) -> OrderResult` method to `OrderService`
- [x] Add structured logging to `pricing_service/services/pricing_service.py`
- [x] Add structured logging to `order_service/services/order_service.py`
- [x] Delete `order_service/tests/test_order_failure.py` (duplicate)
- [x] Update `test_order_service_domain_errors.py` to expect `InvalidOrderRequestError` instead of `ProductNotFoundError`
- [x] Update `test_order_local_validation.py` to expect `InvalidOrderRequestError` instead of `ProductNotFoundError`
- [x] Create `order_service/tests/test_order_service_extended.py` with 5 new tests
- [x] Create `order_service/tests/integration/test_order_get_local.py`
- [x] Create `order_service/tests/test_local_provider.py`
- [x] All 20 tests pass (`uv run pytest -q`)

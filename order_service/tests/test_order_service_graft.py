import json
from decimal import Decimal

import pytest

from order_service.contracts.order_result import OrderResult
from order_service.domain.exceptions import InvalidOrderRequestError, OrderNotFoundError
from order_service.graft.order_service_graft import OrderServiceGraft


class FakeOrderService:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    def place_order(self, product_id, quantity, customer_type):
        if self._error:
            raise self._error
        return self._result

    def get_order(self, order_id):
        if self._error:
            raise self._error
        return self._result


_sample_result = OrderResult(
    order_id="order-1",
    product_id="laptop",
    quantity=2,
    customer_type="premium",
    total_price=Decimal("8500.00"),
    status="CREATED",
)


def test_place_order_returns_json():
    graft = OrderServiceGraft._create_with_service(FakeOrderService(result=_sample_result))
    raw = graft.place_order(product_id="laptop", quantity=2, customer_type="premium")
    data = json.loads(raw)
    assert data["order_id"] == "order-1"
    assert data["total_price"] == "8500.00"
    assert data["status"] == "CREATED"


def test_get_order_returns_json():
    graft = OrderServiceGraft._create_with_service(FakeOrderService(result=_sample_result))
    raw = graft.get_order("order-1")
    data = json.loads(raw)
    assert data["order_id"] == "order-1"
    assert data["product_id"] == "laptop"


def test_place_order_propagates_invalid_request():
    error = InvalidOrderRequestError("unknown product")
    graft = OrderServiceGraft._create_with_service(FakeOrderService(error=error))
    with pytest.raises(InvalidOrderRequestError):
        graft.place_order(product_id="unknown", quantity=1, customer_type="regular")


def test_get_order_propagates_not_found():
    error = OrderNotFoundError("order-999")
    graft = OrderServiceGraft._create_with_service(FakeOrderService(error=error))
    with pytest.raises(OrderNotFoundError):
        graft.get_order("order-999")

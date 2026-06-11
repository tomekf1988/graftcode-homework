from decimal import Decimal

import pytest

from order_service.contracts.pricing_quote import PricingQuote
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    OrderNotFoundError,
)
from order_service.ports.pricing_provider import PricingProvider
from order_service.services.order_service import OrderService

from pricing_service.domain.exceptions import (
    InvalidQuantityError,
    ProductNotFoundError,
    UnsupportedCustomerTypeError,
)


class _RaisingProvider(PricingProvider):
    """Fake provider that raises a specified exception on calculate_price."""

    def __init__(self, exc: Exception):
        self._exc = exc

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:
        raise self._exc


class _SuccessProvider(PricingProvider):
    """Fake provider that always returns a fixed quote."""

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:
        return PricingQuote(
            product_id=product_id,
            unit_price=Decimal("100"),
            quantity=quantity,
            discount_percent=Decimal("0"),
            total_price=Decimal("100") * quantity,
        )


def test_invalid_order_request_raised_for_unknown_product():
    service = OrderService(
        pricing_provider=_RaisingProvider(ProductNotFoundError("product not found")),
    )

    with pytest.raises(InvalidOrderRequestError, match="product not found"):
        service.place_order(product_id="ghost", quantity=1, customer_type="regular")


def test_invalid_order_request_raised_for_invalid_quantity():
    service = OrderService(
        pricing_provider=_RaisingProvider(
            InvalidQuantityError("Quantity must be greater than zero.")
        ),
    )

    with pytest.raises(InvalidOrderRequestError, match="Quantity must be greater than zero"):
        service.place_order(product_id="laptop", quantity=0, customer_type="regular")


def test_invalid_order_request_raised_for_unknown_customer_type():
    service = OrderService(
        pricing_provider=_RaisingProvider(
            UnsupportedCustomerTypeError("Unsupported customer type: 'vip'")
        ),
    )

    with pytest.raises(InvalidOrderRequestError, match="Unsupported customer type"):
        service.place_order(product_id="laptop", quantity=1, customer_type="vip")


def test_get_order_returns_correct_result_after_place_order():
    service = OrderService(pricing_provider=_SuccessProvider())

    placed = service.place_order(
        product_id="laptop",
        quantity=3,
        customer_type="premium",
    )

    retrieved = service.get_order(placed.order_id)

    assert retrieved.order_id == placed.order_id
    assert retrieved.product_id == "laptop"
    assert retrieved.quantity == 3
    assert retrieved.customer_type == "premium"
    assert retrieved.total_price == Decimal("300")
    assert retrieved.status == "CREATED"


def test_get_order_raises_order_not_found_for_unknown_id():
    service = OrderService(pricing_provider=_SuccessProvider())

    with pytest.raises(OrderNotFoundError, match="not found"):
        service.get_order("nonexistent-id")

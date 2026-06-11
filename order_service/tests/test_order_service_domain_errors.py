import pytest

from order_service.services.order_service import OrderService
from order_service.tests.fakes.product_not_found_pricing_provider import (
    ProductNotFoundPricingProvider,
)
from order_service.domain.exceptions import InvalidOrderRequestError


def test_should_raise_invalid_order_request_for_unknown_product():

    service = OrderService(
        pricing_provider=ProductNotFoundPricingProvider(),
    )

    with pytest.raises(InvalidOrderRequestError):
        service.place_order(
            product_id="unknown",
            quantity=1,
            customer_type="premium",
        )

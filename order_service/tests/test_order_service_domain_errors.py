import pytest

from order_service.services.order_service import (
    OrderService,
)
from order_service.tests.fakes.product_not_found_pricing_provider import (
    ProductNotFoundPricingProvider,
)

from pricing_service.domain.exceptions import (
    ProductNotFoundError,
)


def test_should_propagate_product_not_found_error():

    service = OrderService(
        pricing_provider=ProductNotFoundPricingProvider(),
    )

    with pytest.raises(
        ProductNotFoundError,
    ):
        service.place_order(
            product_id="unknown",
            quantity=1,
            customer_type="premium",
        )
from decimal import Decimal

from order_service.adapters.local_pricing_provider import (
    LocalPricingProvider,
)
from order_service.services.order_service import (
    OrderService,
)


def test_should_place_order_using_local_pricing_provider():

    order_service = OrderService(
        pricing_provider=LocalPricingProvider(),
    )

    result = order_service.place_order(
        product_id="laptop",
        quantity=10,
        customer_type="premium",
    )

    assert result.product_id == "laptop"
    assert result.quantity == 10
    assert result.customer_type == "premium"
    assert result.total_price == Decimal("42500")

    assert result.order_id
    assert result.status == "CREATED"
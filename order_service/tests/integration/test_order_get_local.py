from decimal import Decimal

from order_service.adapters.local_pricing_provider import LocalPricingProvider
from order_service.services.order_service import OrderService


def test_get_order_matches_placed_order_via_local_adapter():
    service = OrderService(pricing_provider=LocalPricingProvider())

    placed = service.place_order(
        product_id="laptop",
        quantity=2,
        customer_type="premium",
    )

    retrieved = service.get_order(placed.order_id)

    assert retrieved.order_id == placed.order_id
    assert retrieved.product_id == "laptop"
    assert retrieved.quantity == 2
    assert retrieved.customer_type == "premium"
    assert retrieved.total_price == placed.total_price
    assert retrieved.status == "CREATED"

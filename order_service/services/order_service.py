# order_service.py

from uuid import uuid4

from order_service.contracts.order_result import (
    OrderResult,
)
from order_service.domain.order import Order
from order_service.domain.exceptions import (
    OrderPlacementError,
    PricingServiceUnavailableError,
)
from order_service.ports.pricing_provider import (
    PricingProvider,
)


class OrderService:

    def __init__(
        self,
        pricing_provider: PricingProvider,
    ):
        self._pricing_provider = pricing_provider

    def place_order(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> OrderResult:

        try:
            quote = self._pricing_provider.calculate_price(
                product_id=product_id,
                quantity=quantity,
                customer_type=customer_type,
            )

        except PricingServiceUnavailableError as exc:
            raise OrderPlacementError(
                "Unable to place order because pricing service is unavailable."
            ) from exc

        order = Order(
            order_id=str(uuid4()),
            product_id=product_id,
            quantity=quantity,
            customer_type=customer_type,
            total_price=quote.total_price,
            status="CREATED",
        )

        return OrderResult(
            order_id=order.order_id,
            product_id=order.product_id,
            quantity=order.quantity,
            customer_type=order.customer_type,
            total_price=order.total_price,
            status=order.status,
        )
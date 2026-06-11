import logging
from uuid import uuid4

from order_service.contracts.order_result import OrderResult
from order_service.domain.order import Order
from order_service.domain.exceptions import (
    OrderPlacementError,
    PricingServiceUnavailableError,
    InvalidOrderRequestError,
    OrderNotFoundError,
)
from order_service.ports.pricing_provider import PricingProvider

from pricing_service.domain.exceptions import (
    ProductNotFoundError,
    InvalidQuantityError,
    UnsupportedCustomerTypeError,
)

logger = logging.getLogger(__name__)


class OrderService:

    def __init__(
        self,
        pricing_provider: PricingProvider,
    ):
        self._pricing_provider = pricing_provider
        self._orders: dict[str, Order] = {}

    def place_order(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> OrderResult:

        logger.info(
            "Placing order product=%s qty=%s customer=%s",
            product_id,
            quantity,
            customer_type,
        )

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

        except (
            ProductNotFoundError,
            InvalidQuantityError,
            UnsupportedCustomerTypeError,
        ) as exc:
            logger.warning("Invalid order request: %s", exc)
            raise InvalidOrderRequestError(str(exc)) from exc

        order = Order(
            order_id=str(uuid4()),
            product_id=product_id,
            quantity=quantity,
            customer_type=customer_type,
            total_price=quote.total_price,
            status="CREATED",
        )

        self._orders[order.order_id] = order

        logger.info(
            "Order created order_id=%s total=%s",
            order.order_id,
            order.total_price,
        )

        return OrderResult(
            order_id=order.order_id,
            product_id=order.product_id,
            quantity=order.quantity,
            customer_type=order.customer_type,
            total_price=order.total_price,
            status=order.status,
        )

    def get_order(self, order_id: str) -> OrderResult:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order '{order_id}' not found.")
        return OrderResult(
            order_id=order.order_id,
            product_id=order.product_id,
            quantity=order.quantity,
            customer_type=order.customer_type,
            total_price=order.total_price,
            status=order.status,
        )

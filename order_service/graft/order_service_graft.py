import json
import logging

from order_service.bootstrap.factory import create_order_service
from order_service.config.settings import load_settings
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    InvalidQuantityError,
    OrderNotFoundError,
    OrderPlacementError,
    PricingServiceUnavailableError,
    ProductNotFoundError,
    UnsupportedCustomerTypeError,
)

logger = logging.getLogger(__name__)


class OrderServiceGraft:

    def __init__(self):
        settings = load_settings()
        self._service = create_order_service(settings)

    @classmethod
    def _create_with_service(cls, service):
        instance = cls.__new__(cls)
        instance._service = service
        return instance

    def place_order(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> str:
        try:
            result = self._service.place_order(
                product_id=product_id,
                quantity=quantity,
                customer_type=customer_type,
            )
        except (ProductNotFoundError, InvalidQuantityError, UnsupportedCustomerTypeError) as e:
            logger.warning("Invalid order request: %s", e)
            raise
        except InvalidOrderRequestError as e:
            logger.warning("Invalid order request: %s", e)
            raise
        except (PricingServiceUnavailableError, OrderPlacementError) as e:
            logger.error("Order placement failed: %s", e)
            raise

        return json.dumps({
            "order_id": result.order_id,
            "product_id": result.product_id,
            "quantity": result.quantity,
            "customer_type": result.customer_type,
            "total_price": str(result.total_price),
            "status": result.status,
        })

    def get_order(self, order_id: str) -> str:
        try:
            result = self._service.get_order(order_id)
        except OrderNotFoundError as e:
            logger.warning("Order not found: %s", e)
            raise

        return json.dumps({
            "order_id": result.order_id,
            "product_id": result.product_id,
            "quantity": result.quantity,
            "customer_type": result.customer_type,
            "total_price": str(result.total_price),
            "status": result.status,
        })

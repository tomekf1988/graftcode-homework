import json

from order_service.bootstrap.factory import create_order_service
from order_service.config.settings import load_settings


class OrderServiceGraft:

    def __init__(self):
        settings = load_settings()
        self._service = create_order_service(settings)

    def place_order(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> str:

        result = self._service.place_order(
            product_id=product_id,
            quantity=quantity,
            customer_type=customer_type,
        )

        return json.dumps({
            "order_id": result.order_id,
            "product_id": result.product_id,
            "quantity": result.quantity,
            "customer_type": result.customer_type,
            "total_price": str(result.total_price),
            "status": result.status,
        })

    def get_order(self, order_id: str) -> str:

        result = self._service.get_order(order_id)

        return json.dumps({
            "order_id": result.order_id,
            "product_id": result.product_id,
            "quantity": result.quantity,
            "customer_type": result.customer_type,
            "total_price": str(result.total_price),
            "status": result.status,
        })

from order_service.domain.exceptions import InvalidOrderRequestError
from order_service.ports.pricing_provider import PricingProvider


class ProductNotFoundPricingProvider(PricingProvider):

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ):
        raise InvalidOrderRequestError(
            f"Product '{product_id}' not found."
        )

from order_service.ports.pricing_provider import PricingProvider

from pricing_service.domain.exceptions import (
    ProductNotFoundError,
)


class ProductNotFoundPricingProvider(PricingProvider):

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ):
        raise ProductNotFoundError(
            f"Product {product_id} not found"
        )
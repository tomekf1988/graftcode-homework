from typing import Protocol

from order_service.contracts.pricing_quote import PricingQuote


class PricingProvider(Protocol):

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:
        ...
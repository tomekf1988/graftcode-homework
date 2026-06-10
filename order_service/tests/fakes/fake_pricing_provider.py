from decimal import Decimal

from order_service.contracts.pricing_quote import PricingQuote
from order_service.ports.pricing_provider import PricingProvider


class FakePricingProvider(PricingProvider):

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:
        return PricingQuote(
            product_id=product_id,
            unit_price=Decimal("5000"),
            quantity=quantity,
            discount_percent=Decimal("15"),
            total_price=Decimal("42500"),
        )
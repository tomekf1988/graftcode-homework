from order_service.contracts.pricing_quote import PricingQuote
from order_service.ports.pricing_provider import PricingProvider

from pricing_service.bootstrap.factory import (
    create_pricing_service,
)
from pricing_service.domain.customer_type import CustomerType
from pricing_service.contracts.price_calculation_input import (
    PriceCalculationInput,
)


class LocalPricingProvider(PricingProvider):

    def __init__(self):
        self._pricing_service = create_pricing_service()

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:

        result = self._pricing_service.calculate_price(
            PriceCalculationInput(
                product_id=product_id,
                quantity=quantity,
                customer_type=CustomerType(customer_type),
            )
        )

        return PricingQuote(
            product_id=result.product_id,
            unit_price=result.unit_price,
            quantity=result.quantity,
            discount_percent=result.discount_percent,
            total_price=result.total_price,
        )
import json

from pricing_service.bootstrap.factory import create_pricing_service
from pricing_service.contracts.price_calculation_input import (
    PriceCalculationInput,
)


class PricingServiceGraft:

    def __init__(self):
        self._pricing_service = create_pricing_service()

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> str:

        result = self._pricing_service.calculate_price(
            PriceCalculationInput(
                product_id=product_id,
                quantity=quantity,
                customer_type=customer_type,
            )
        )

        return json.dumps(result.to_dict())
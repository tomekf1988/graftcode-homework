from dataclasses import dataclass

from pricing_service.domain.customer_type import CustomerType


@dataclass(frozen=True)
class PriceCalculationInput:
    product_id: str
    quantity: int
    customer_type: CustomerType
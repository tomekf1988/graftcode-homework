from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PriceCalculationResult:
    product_id: str
    unit_price: Decimal
    quantity: int
    discount_percent: Decimal
    total_price: Decimal
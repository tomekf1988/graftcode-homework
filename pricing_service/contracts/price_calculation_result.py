from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PriceCalculationResult:
    product_id: str
    unit_price: Decimal
    quantity: int
    discount_percent: Decimal
    total_price: Decimal

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "unit_price": str(self.unit_price),
            "quantity": self.quantity,
            "discount_percent": str(self.discount_percent),
            "total_price": str(self.total_price),
        }
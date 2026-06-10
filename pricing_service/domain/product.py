from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Product:
    id: str
    name: str
    unit_price: Decimal
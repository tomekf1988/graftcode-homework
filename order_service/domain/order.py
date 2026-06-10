from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Order:
    order_id: str
    product_id: str
    quantity: int
    customer_type: str
    total_price: Decimal
    status: str
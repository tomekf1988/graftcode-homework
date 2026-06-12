from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from order_service.contracts.order_result import OrderResult


class PlaceOrderRequest(BaseModel):
    product_id: str
    quantity: int
    customer_type: str


class OrderResponse(BaseModel):
    order_id: str
    product_id: str
    quantity: int
    customer_type: str
    total_price: Decimal
    status: str

    @classmethod
    def from_result(cls, result: OrderResult) -> OrderResponse:
        return cls(
            order_id=result.order_id,
            product_id=result.product_id,
            quantity=result.quantity,
            customer_type=result.customer_type,
            total_price=result.total_price,
            status=result.status,
        )

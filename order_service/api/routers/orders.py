from fastapi import APIRouter, Depends

from order_service.api.dependencies import get_order_service
from order_service.api.schemas import OrderResponse, PlaceOrderRequest
from order_service.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def place_order(
    body: PlaceOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return OrderResponse.from_result(
        service.place_order(
            product_id=body.product_id,
            quantity=body.quantity,
            customer_type=body.customer_type,
        )
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return OrderResponse.from_result(service.get_order(order_id))

from fastapi import APIRouter, Request

from order_service.api.schemas import OrderResponse, PlaceOrderRequest

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def place_order(body: PlaceOrderRequest, request: Request) -> OrderResponse:
    result = request.app.state.order_service.place_order(
        product_id=body.product_id,
        quantity=body.quantity,
        customer_type=body.customer_type,
    )
    return OrderResponse.from_result(result)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, request: Request) -> OrderResponse:
    result = request.app.state.order_service.get_order(order_id)
    return OrderResponse.from_result(result)

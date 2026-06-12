from fastapi import Request

from order_service.services.order_service import OrderService


def get_order_service(request: Request) -> OrderService:
    return request.app.state.order_service

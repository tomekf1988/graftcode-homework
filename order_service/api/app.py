from contextlib import asynccontextmanager

from fastapi import FastAPI

from order_service.api.error_handlers import (
    invalid_order_request_handler,
    order_not_found_handler,
    order_placement_handler,
)
from order_service.api.routers.orders import router as orders_router
from order_service.bootstrap.factory import create_order_service
from order_service.config.settings import load_settings
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    OrderNotFoundError,
    OrderPlacementError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.order_service = create_order_service(load_settings())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Order Service", lifespan=lifespan)

    app.add_exception_handler(InvalidOrderRequestError, invalid_order_request_handler)
    app.add_exception_handler(OrderNotFoundError, order_not_found_handler)
    app.add_exception_handler(OrderPlacementError, order_placement_handler)

    app.include_router(orders_router)

    return app


app = create_app()

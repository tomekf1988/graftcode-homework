from fastapi import Request
from fastapi.responses import JSONResponse

from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    OrderNotFoundError,
    OrderPlacementError,
)


async def invalid_order_request_handler(
    _request: Request, exc: InvalidOrderRequestError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def order_not_found_handler(
    _request: Request, exc: OrderNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def order_placement_handler(
    _request: Request, exc: OrderPlacementError
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})

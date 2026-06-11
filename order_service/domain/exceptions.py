class OrderError(Exception):
    pass


class OrderPlacementError(OrderError):
    pass


class PricingServiceUnavailableError(OrderError):
    pass


class PricingServiceTimeoutError(OrderError):
    pass


class InvalidOrderRequestError(OrderError):
    pass


class OrderNotFoundError(OrderError):
    pass
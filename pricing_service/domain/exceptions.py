class PricingError(Exception):
    pass


class ProductNotFoundError(PricingError):
    pass


class InvalidQuantityError(PricingError):
    pass
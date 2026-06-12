import logging
from decimal import Decimal

from pricing_service.domain.customer_type import CustomerType
from pricing_service.domain.exceptions import (
    InvalidQuantityError,
    ProductNotFoundError,
    UnsupportedCustomerTypeError,
)
from pricing_service.domain.pricing_rules import PricingRulesEngine
from pricing_service.domain.product_catalog import ProductCatalog
from pricing_service.contracts.price_calculation_input import PriceCalculationInput
from pricing_service.contracts.price_calculation_result import PriceCalculationResult

logger = logging.getLogger(__name__)


class PricingService:

    def __init__(
        self,
        product_catalog: ProductCatalog,
        pricing_rules_engine: PricingRulesEngine,
    ):
        self._product_catalog = product_catalog
        self._pricing_rules_engine = pricing_rules_engine

    def calculate_price(
        self,
        request: PriceCalculationInput,
    ) -> PriceCalculationResult:

        logger.info(
            "Calculating price for product=%s qty=%s customer=%s",
            request.product_id,
            request.quantity,
            request.customer_type,
        )

        try:
            CustomerType(request.customer_type)
        except ValueError:
            raise UnsupportedCustomerTypeError(
                f"Unsupported customer type: '{request.customer_type}'."
            )

        if request.quantity <= 0:
            raise InvalidQuantityError(
                "Quantity must be greater than zero."
            )

        product = self._product_catalog.get(
            request.product_id,
        )

        if product is None:
            raise ProductNotFoundError(
                f"Product '{request.product_id}' not found."
            )

        discount_percent = (
            self._pricing_rules_engine
            .calculate_discount_percent(request)
        )

        subtotal = (
            product.unit_price
            * request.quantity
        )

        discount_multiplier = (
            Decimal("100") - Decimal(discount_percent)
        ) / Decimal("100")

        total_price = (
            subtotal * discount_multiplier
        )

        logger.debug(
            "Applied discount=%s%% total=%s",
            discount_percent,
            total_price,
        )

        return PriceCalculationResult(
            product_id=product.id,
            unit_price=product.unit_price,
            quantity=request.quantity,
            discount_percent=Decimal(discount_percent),
            total_price=total_price,
        )
from typing import Protocol

from pricing_service.domain.customer_type import CustomerType
from pricing_service.contracts.price_calculation_input import PriceCalculationInput


class PricingRule(Protocol):

    def discount_percent(
        self,
        request: PriceCalculationInput,
    ) -> int:
        ...


class PremiumCustomerRule:

    def discount_percent(
        self,
        request: PriceCalculationInput,
    ) -> int:

        if request.customer_type == CustomerType.PREMIUM:
            return 10

        return 0


class BulkOrderRule:

    def discount_percent(
        self,
        request: PriceCalculationInput,
    ) -> int:

        if request.quantity >= 10:
            return 5

        return 0


class PricingRulesEngine:

    MAX_DISCOUNT_PERCENT = 20

    def __init__(
        self,
        rules: list[PricingRule],
    ):
        self._rules = rules

    def calculate_discount_percent(
        self,
        request: PriceCalculationInput,
    ) -> int:

        total_discount = sum(
            rule.discount_percent(request)
            for rule in self._rules
        )

        return min(
            total_discount,
            self.MAX_DISCOUNT_PERCENT,
        )
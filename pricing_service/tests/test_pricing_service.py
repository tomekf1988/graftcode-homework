import pytest

from decimal import Decimal

from pricing_service.domain.customer_type import CustomerType
from pricing_service.domain.exceptions import (
    InvalidQuantityError,
    ProductNotFoundError,
    UnsupportedCustomerTypeError,
)
from pricing_service.contracts.price_calculation_input import (
    PriceCalculationInput,
)
from pricing_service.domain.pricing_rules import (
    BulkOrderRule,
    PremiumCustomerRule,
    PricingRulesEngine,
)
from pricing_service.services.pricing_service import PricingService
from pricing_service.domain.product_catalog import ProductCatalog


@pytest.fixture
def pricing_service() -> PricingService:
    catalog = ProductCatalog()

    rules_engine = PricingRulesEngine(
        rules=[
            PremiumCustomerRule(),
            BulkOrderRule(),
        ]
    )

    return PricingService(
        product_catalog=catalog,
        pricing_rules_engine=rules_engine,
    )


def test_should_calculate_price_for_regular_customer(
    pricing_service: PricingService,
):
    result = pricing_service.calculate_price(
        PriceCalculationInput(
            product_id="laptop",
            quantity=1,
            customer_type=CustomerType.REGULAR,
        )
    )

    assert result.discount_percent == Decimal("0")
    assert result.total_price == Decimal("5000")


def test_should_apply_premium_discount(
    pricing_service: PricingService,
):
    result = pricing_service.calculate_price(
        PriceCalculationInput(
            product_id="laptop",
            quantity=1,
            customer_type=CustomerType.PREMIUM,
        )
    )

    assert result.discount_percent == Decimal("10")
    assert result.total_price == Decimal("4500")


def test_should_apply_bulk_discount(
    pricing_service: PricingService,
):
    result = pricing_service.calculate_price(
        PriceCalculationInput(
            product_id="laptop",
            quantity=10,
            customer_type=CustomerType.REGULAR,
        )
    )

    assert result.discount_percent == Decimal("5")
    assert result.total_price == Decimal("47500")


def test_should_combine_premium_and_bulk_discount(
    pricing_service: PricingService,
):
    result = pricing_service.calculate_price(
        PriceCalculationInput(
            product_id="laptop",
            quantity=10,
            customer_type=CustomerType.PREMIUM,
        )
    )

    assert result.discount_percent == Decimal("15")
    assert result.total_price == Decimal("42500")


def test_should_raise_for_unknown_product(
    pricing_service: PricingService,
):
    with pytest.raises(ProductNotFoundError):
        pricing_service.calculate_price(
            PriceCalculationInput(
                product_id="unknown",
                quantity=1,
                customer_type=CustomerType.REGULAR,
            )
        )


def test_should_raise_for_unsupported_customer_type(
    pricing_service: PricingService,
):
    with pytest.raises(UnsupportedCustomerTypeError):
        pricing_service.calculate_price(
            PriceCalculationInput(
                product_id="laptop",
                quantity=1,
                customer_type="vip",
            )
        )


def test_should_raise_for_zero_quantity(
    pricing_service: PricingService,
):
    with pytest.raises(InvalidQuantityError):
        pricing_service.calculate_price(
            PriceCalculationInput(
                product_id="laptop",
                quantity=0,
                customer_type=CustomerType.REGULAR,
            )
        )

class FakeDiscountRule:

    def discount_percent(
        self,
        request,
    ) -> int:
        return 15


def test_should_cap_discount_at_twenty_percent():

    rules_engine = PricingRulesEngine(
        rules=[
            PremiumCustomerRule(),
            BulkOrderRule(),
            FakeDiscountRule(),
        ]
    )

    discount = rules_engine.calculate_discount_percent(
        PriceCalculationInput(
            product_id="laptop",
            quantity=10,
            customer_type=CustomerType.PREMIUM,
        )
    )

    assert discount == 20
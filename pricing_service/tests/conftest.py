import pytest

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
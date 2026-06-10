from pricing_service.domain.pricing_rules import (
    BulkOrderRule,
    PremiumCustomerRule,
    PricingRulesEngine,
)
from pricing_service.services.pricing_service import PricingService
from pricing_service.domain.product_catalog import ProductCatalog


def create_pricing_service() -> PricingService:

    return PricingService(
        product_catalog=ProductCatalog(),
        pricing_rules_engine=PricingRulesEngine(
            rules=[
                PremiumCustomerRule(),
                BulkOrderRule(),
            ]
        ),
    )
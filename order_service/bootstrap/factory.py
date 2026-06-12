from order_service.adapters.graft_pricing_provider import GraftPricingProvider
from order_service.config.settings import Settings
from order_service.services.order_service import OrderService


def create_order_service(settings: Settings) -> OrderService:
    return OrderService(
        pricing_provider=GraftPricingProvider(host=settings.graft_host),
    )

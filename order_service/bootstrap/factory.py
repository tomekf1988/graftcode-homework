from order_service.adapters.local_pricing_provider import (
    LocalPricingProvider,
)
from order_service.adapters.remote_pricing_provider import (
    RemotePricingProvider,
)
from order_service.config.pricing_mode import PricingMode
from order_service.config.settings import Settings
from order_service.services.order_service import OrderService


def create_order_service(
    mode: PricingMode,
) -> OrderService:

    if mode == PricingMode.LOCAL:
        return OrderService(
            pricing_provider=LocalPricingProvider(),
        )

    if mode == PricingMode.REMOTE:
        return OrderService(
            pricing_provider=RemotePricingProvider(),
        )

    raise ValueError(
        f"Unsupported mode: {mode}"
    )


def create_order_service_from_settings(settings: Settings) -> OrderService:
    return create_order_service(settings.pricing_mode)
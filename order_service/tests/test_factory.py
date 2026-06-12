from unittest.mock import patch, MagicMock

from order_service.bootstrap.factory import create_order_service_from_settings
from order_service.config.pricing_mode import PricingMode
from order_service.config.settings import Settings
from order_service.services.order_service import OrderService


@patch("order_service.bootstrap.factory.GraftPricingProvider")
def test_returns_order_service_instance(mock_provider_cls):
    mock_provider_cls.return_value = MagicMock()

    settings = Settings(pricing_mode=PricingMode.LOCAL)
    service = create_order_service_from_settings(settings)

    assert isinstance(service, OrderService)


@patch("order_service.bootstrap.factory.GraftPricingProvider")
def test_creates_graft_provider_regardless_of_mode(mock_provider_cls):
    mock_provider_cls.return_value = MagicMock()

    for mode in PricingMode:
        create_order_service_from_settings(Settings(pricing_mode=mode))

    assert mock_provider_cls.call_count == len(list(PricingMode))

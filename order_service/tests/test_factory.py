from unittest.mock import patch, MagicMock

from order_service.bootstrap.factory import create_order_service
from order_service.config.settings import Settings
from order_service.services.order_service import OrderService


@patch("order_service.bootstrap.factory.GraftPricingProvider")
def test_returns_order_service_instance(mock_provider_cls):
    mock_provider_cls.return_value = MagicMock()

    service = create_order_service(Settings(pricing_mode="remote", graft_host=None))

    assert isinstance(service, OrderService)


@patch("order_service.bootstrap.factory.GraftPricingProvider")
def test_remote_mode_passes_host_to_provider(mock_provider_cls):
    mock_provider_cls.return_value = MagicMock()

    create_order_service(Settings(pricing_mode="remote", graft_host="ws://pricing/ws"))

    mock_provider_cls.assert_called_once_with(host="ws://pricing/ws")


@patch("order_service.bootstrap.factory.GraftPricingProvider")
def test_local_mode_passes_none_host_to_provider(mock_provider_cls):
    mock_provider_cls.return_value = MagicMock()

    create_order_service(Settings(pricing_mode="local", graft_host="ws://pricing/ws"))

    mock_provider_cls.assert_called_once_with(host=None)

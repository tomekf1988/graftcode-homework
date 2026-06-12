import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from hypertube.utils.exception.HypertubeException import HypertubeException

from order_service.adapters.graft_pricing_provider import GraftPricingProvider
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    PricingServiceUnavailableError,
)


def _make_provider(mock_client: MagicMock) -> GraftPricingProvider:
    with patch("order_service.adapters.graft_pricing_provider.PricingServiceGraft", return_value=mock_client), \
         patch("order_service.adapters.graft_pricing_provider.GraftConfig"):
        return GraftPricingProvider()


def _price_json(**overrides) -> str:
    data = {
        "product_id": "laptop",
        "unit_price": "5000",
        "quantity": 2,
        "discount_percent": "10",
        "total_price": "9000",
    }
    data.update(overrides)
    return json.dumps(data)


def test_maps_json_response_to_pricing_quote():
    client = MagicMock()
    client.calculate_price.return_value = _price_json()
    provider = _make_provider(client)

    quote = provider.calculate_price("laptop", 2, "premium")

    assert quote.product_id == "laptop"
    assert quote.unit_price == Decimal("5000")
    assert quote.quantity == 2
    assert quote.discount_percent == Decimal("10")
    assert quote.total_price == Decimal("9000")


def test_hypertube_exception_raises_invalid_order_request():
    client = MagicMock()
    client.calculate_price.side_effect = HypertubeException(
        name="Exception",
        message="Product 'unknown' not found.",
        traceback_str="",
    )
    provider = _make_provider(client)

    with pytest.raises(InvalidOrderRequestError, match="Product 'unknown' not found."):
        provider.calculate_price("unknown", 1, "regular")


def test_connection_error_raises_pricing_service_unavailable():
    client = MagicMock()
    client.calculate_price.side_effect = ConnectionError("gateway down")
    provider = _make_provider(client)

    with pytest.raises(PricingServiceUnavailableError):
        provider.calculate_price("laptop", 1, "regular")


def test_generic_exception_raises_pricing_service_unavailable():
    client = MagicMock()
    client.calculate_price.side_effect = RuntimeError("unexpected")
    provider = _make_provider(client)

    with pytest.raises(PricingServiceUnavailableError):
        provider.calculate_price("laptop", 1, "regular")

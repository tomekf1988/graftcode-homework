import json
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from hypertube.utils.exception.HypertubeException import HypertubeException

from order_service.adapters.graft_pricing_provider import GraftPricingProvider
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    InvalidQuantityError,
    ProductNotFoundError,
    PricingServiceUnavailableError,
    UnsupportedCustomerTypeError,
)


def _provider(mock_client: MagicMock) -> GraftPricingProvider:
    return GraftPricingProvider(client=mock_client)


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
    provider = _provider(client)

    quote = provider.calculate_price("laptop", 2, "premium")

    assert quote.product_id == "laptop"
    assert quote.unit_price == Decimal("5000")
    assert quote.quantity == 2
    assert quote.discount_percent == Decimal("10")
    assert quote.total_price == Decimal("9000")


def test_hypertube_exception_raises_invalid_order_request_for_unknown_name():
    client = MagicMock()
    client.calculate_price.side_effect = HypertubeException(
        name="SomeUnknownError",
        message="something went wrong",
        traceback_str="",
    )
    provider = _provider(client)

    with pytest.raises(InvalidOrderRequestError):
        provider.calculate_price("laptop", 1, "regular")


def test_product_not_found_error_mapped_by_name():
    client = MagicMock()
    client.calculate_price.side_effect = HypertubeException(
        name="ProductNotFoundError",
        message="Product 'x' not found.",
        traceback_str="",
    )
    with pytest.raises(ProductNotFoundError, match="Product 'x' not found."):
        _provider(client).calculate_price("x", 1, "regular")


def test_invalid_quantity_error_mapped_by_name():
    client = MagicMock()
    client.calculate_price.side_effect = HypertubeException(
        name="InvalidQuantityError",
        message="Quantity must be positive.",
        traceback_str="",
    )
    with pytest.raises(InvalidQuantityError):
        _provider(client).calculate_price("laptop", 0, "regular")


def test_unsupported_customer_type_error_mapped_by_name():
    client = MagicMock()
    client.calculate_price.side_effect = HypertubeException(
        name="UnsupportedCustomerTypeError",
        message="Unsupported customer type: vip",
        traceback_str="",
    )
    with pytest.raises(UnsupportedCustomerTypeError):
        _provider(client).calculate_price("laptop", 1, "vip")


def test_connection_error_raises_pricing_service_unavailable():
    client = MagicMock()
    client.calculate_price.side_effect = ConnectionError("gateway down")
    provider = _provider(client)

    with pytest.raises(PricingServiceUnavailableError):
        provider.calculate_price("laptop", 1, "regular")


def test_generic_exception_raises_pricing_service_unavailable():
    client = MagicMock()
    client.calculate_price.side_effect = RuntimeError("unexpected")
    provider = _provider(client)

    with pytest.raises(PricingServiceUnavailableError):
        provider.calculate_price("laptop", 1, "regular")

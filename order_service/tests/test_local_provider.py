import pytest

from order_service.adapters.local_pricing_provider import LocalPricingProvider
from pricing_service.domain.exceptions import UnsupportedCustomerTypeError


def test_unknown_customer_type_raises_unsupported_customer_type_error():
    provider = LocalPricingProvider()

    with pytest.raises(UnsupportedCustomerTypeError, match="Unsupported customer type"):
        provider.calculate_price(
            product_id="laptop",
            quantity=1,
            customer_type="unknown_type",
        )

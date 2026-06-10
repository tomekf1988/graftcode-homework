import pytest

from order_service.bootstrap.factory import (
    create_order_service,
)
from order_service.config.pricing_mode import (
    PricingMode,
)

from pricing_service.domain.exceptions import (
    ProductNotFoundError,
)


def test_should_fail_for_unknown_product():

    service = create_order_service(
        PricingMode.LOCAL,
    )

    with pytest.raises(
        ProductNotFoundError,
    ):
        service.place_order(
            product_id="unknown",
            quantity=1,
            customer_type="premium",
        )
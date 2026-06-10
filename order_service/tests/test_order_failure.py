import pytest

from order_service.bootstrap.factory import (
    create_order_service,
)
from order_service.domain.exceptions import (
    OrderPlacementError,
)


def test_should_raise_order_placement_error_when_pricing_is_unavailable():

    service = create_order_service(
        mode="remote",
    )

    with pytest.raises(
        OrderPlacementError,
        match="pricing service is unavailable",
    ):
        service.place_order(
            product_id="laptop",
            quantity=1,
            customer_type="premium",
        )
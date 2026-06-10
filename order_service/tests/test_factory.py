from order_service.bootstrap.factory import (
    create_order_service,
)
from order_service.config.pricing_mode import (
    PricingMode,
)


def test_should_create_order_service_for_local_mode():

    service = create_order_service(
        mode=PricingMode.LOCAL,
    )

    assert service is not None
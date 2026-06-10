import logging
import time

from order_service.domain.exceptions import (
    PricingServiceUnavailableError,
)
from order_service.contracts.pricing_quote import PricingQuote
from order_service.ports.pricing_provider import PricingProvider


logger = logging.getLogger(__name__)


class RemotePricingProvider(PricingProvider):

    MAX_RETRIES = 3

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:

        for attempt in range(1, self.MAX_RETRIES + 1):

            try:
                logger.info(
                    "Calling remote pricing service. Attempt %s",
                    attempt,
                )

                raise ConnectionError()

            except ConnectionError:

                logger.warning(
                    "Pricing service unavailable. Attempt %s/%s",
                    attempt,
                    self.MAX_RETRIES,
                )

                if attempt == self.MAX_RETRIES:
                    raise PricingServiceUnavailableError(
                        "Pricing Service is unavailable."
                    )

                time.sleep(0.1)

        raise RuntimeError("Unreachable")
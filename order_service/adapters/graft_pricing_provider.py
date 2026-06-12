import json
import logging
from decimal import Decimal

from graft_pypi_pricing_service_graft.graft.pypi.pricing_service_graft.graft_config import GraftConfig
from graft_pypi_pricing_service_graft.pricingservicegraft import PricingServiceGraft
from hypertube.utils.exception.HypertubeException import HypertubeException

from order_service.contracts.pricing_quote import PricingQuote
from order_service.domain.exceptions import (
    InvalidOrderRequestError,
    PricingServiceUnavailableError,
)
from order_service.ports.pricing_provider import PricingProvider

logger = logging.getLogger(__name__)


class GraftPricingProvider(PricingProvider):

    def __init__(self, host: str | None = None, client: PricingServiceGraft | None = None):
        if host:
            GraftConfig.host = host
        self._client = client or PricingServiceGraft()

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingQuote:

        try:
            result_json = self._client.calculate_price(
                product_id,
                quantity,
                customer_type,
            )
            result = json.loads(result_json)
            return PricingQuote(
                product_id=result["product_id"],
                unit_price=Decimal(result["unit_price"]),
                quantity=result["quantity"],
                discount_percent=Decimal(result["discount_percent"]),
                total_price=Decimal(result["total_price"]),
            )

        except HypertubeException as exc:
            logger.warning("Pricing domain error: %s", exc.message)
            raise InvalidOrderRequestError(exc.message) from exc

        except Exception as exc:
            logger.error("Pricing service unavailable: %s", exc)
            raise PricingServiceUnavailableError(
                "Pricing service is unavailable."
            ) from exc

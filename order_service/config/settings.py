import os
from dataclasses import dataclass

from order_service.config.pricing_mode import PricingMode


@dataclass(frozen=True)
class Settings:
    pricing_mode: PricingMode


def load_settings() -> Settings:
    raw_mode = os.environ.get("PRICING_MODE", "local").lower()

    try:
        pricing_mode = PricingMode(raw_mode)
    except ValueError:
        valid = ", ".join(m.value for m in PricingMode)
        raise ValueError(
            f"Invalid PRICING_MODE={raw_mode!r}. Valid values are: {valid}"
        )

    return Settings(pricing_mode=pricing_mode)

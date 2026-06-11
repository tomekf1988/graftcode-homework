import os
from dataclasses import dataclass

from order_service.config.pricing_mode import PricingMode


@dataclass(frozen=True)
class Settings:
    pricing_mode: PricingMode
    # Validated at startup when PRICING_MODE=remote.
    # RemotePricingProvider reads GRAFTCODE_PROJECT_KEY directly from the
    # environment — it is not injected via this dataclass yet. Passing it
    # through is deferred to the milestone that wires up the remote provider.
    graftcode_project_key: str | None


def load_settings() -> Settings:
    raw_mode = os.environ.get("PRICING_MODE", "local").lower()

    try:
        pricing_mode = PricingMode(raw_mode)
    except ValueError:
        valid = ", ".join(m.value for m in PricingMode)
        raise ValueError(
            f"Invalid PRICING_MODE={raw_mode!r}. Valid values are: {valid}"
        )

    graftcode_project_key = os.environ.get("GRAFTCODE_PROJECT_KEY") or None

    if pricing_mode == PricingMode.REMOTE and graftcode_project_key is None:
        raise ValueError(
            "GRAFTCODE_PROJECT_KEY must be set when PRICING_MODE=remote"
        )

    return Settings(
        pricing_mode=pricing_mode,
        graftcode_project_key=graftcode_project_key,
    )

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    pricing_mode: str
    graft_host: str | None


_VALID_PRICING_MODES = {"remote", "local"}


def load_settings() -> Settings:
    pricing_mode = os.environ.get("PRICING_MODE", "remote").lower()
    if pricing_mode not in _VALID_PRICING_MODES:
        raise ValueError(
            f"Invalid PRICING_MODE={pricing_mode!r}. Expected one of: {sorted(_VALID_PRICING_MODES)}"
        )
    return Settings(
        pricing_mode=pricing_mode,
        graft_host=os.environ.get("GRAFT_HOST"),
    )

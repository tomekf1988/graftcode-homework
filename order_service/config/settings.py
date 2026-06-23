import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    pricing_mode: str
    graft_host: str | None


def load_settings() -> Settings:
    return Settings(
        pricing_mode=os.environ.get("PRICING_MODE", "remote").lower(),
        graft_host=os.environ.get("GRAFT_HOST"),
    )

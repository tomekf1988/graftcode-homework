import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    graft_host: str | None


def load_settings() -> Settings:
    return Settings(graft_host=os.environ.get("GRAFT_HOST"))

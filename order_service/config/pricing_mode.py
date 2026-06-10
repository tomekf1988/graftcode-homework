from enum import Enum


class PricingMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
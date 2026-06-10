from enum import Enum


class CustomerType(str, Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
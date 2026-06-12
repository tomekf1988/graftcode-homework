import pytest

from order_service.config.pricing_mode import PricingMode
from order_service.config.settings import Settings, load_settings


def test_defaults_to_local_mode(monkeypatch):
    monkeypatch.delenv("PRICING_MODE", raising=False)

    settings = load_settings()

    assert settings == Settings(pricing_mode=PricingMode.LOCAL)


def test_remote_mode(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "remote")

    settings = load_settings()

    assert settings == Settings(pricing_mode=PricingMode.REMOTE)


def test_invalid_pricing_mode_raises(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "cloud")

    with pytest.raises(ValueError, match="PRICING_MODE"):
        load_settings()


def test_pricing_mode_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "LOCAL")

    settings = load_settings()

    assert settings.pricing_mode == PricingMode.LOCAL

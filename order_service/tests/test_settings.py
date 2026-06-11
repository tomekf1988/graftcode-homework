import pytest

from order_service.config.pricing_mode import PricingMode
from order_service.config.settings import Settings, load_settings


def test_defaults_when_no_env_vars_set(monkeypatch):
    monkeypatch.delenv("PRICING_MODE", raising=False)
    monkeypatch.delenv("GRAFTCODE_PROJECT_KEY", raising=False)

    settings = load_settings()

    assert settings == Settings(
        pricing_mode=PricingMode.LOCAL,
        graftcode_project_key=None,
    )


def test_remote_mode_with_project_key(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "remote")
    monkeypatch.setenv("GRAFTCODE_PROJECT_KEY", "test-key")

    settings = load_settings()

    assert settings == Settings(
        pricing_mode=PricingMode.REMOTE,
        graftcode_project_key="test-key",
    )


def test_remote_mode_without_project_key_raises(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "remote")
    monkeypatch.delenv("GRAFTCODE_PROJECT_KEY", raising=False)

    with pytest.raises(ValueError, match="GRAFTCODE_PROJECT_KEY"):
        load_settings()


def test_invalid_pricing_mode_raises(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "cloud")
    monkeypatch.delenv("GRAFTCODE_PROJECT_KEY", raising=False)

    with pytest.raises(ValueError, match="PRICING_MODE"):
        load_settings()


def test_pricing_mode_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "LOCAL")
    monkeypatch.delenv("GRAFTCODE_PROJECT_KEY", raising=False)

    settings = load_settings()

    assert settings.pricing_mode == PricingMode.LOCAL


def test_remote_mode_with_blank_project_key_raises(monkeypatch):
    # An empty string is treated the same as absent — both are invalid for remote mode.
    monkeypatch.setenv("PRICING_MODE", "remote")
    monkeypatch.setenv("GRAFTCODE_PROJECT_KEY", "")

    with pytest.raises(ValueError, match="GRAFTCODE_PROJECT_KEY"):
        load_settings()

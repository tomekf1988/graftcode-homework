import pytest

from order_service.config.settings import Settings, load_settings


def test_remote_mode_with_host(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "remote")
    monkeypatch.setenv("GRAFT_HOST", "ws://localhost/ws")

    settings = load_settings()

    assert settings == Settings(pricing_mode="remote", graft_host="ws://localhost/ws")


def test_local_mode(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "local")
    monkeypatch.delenv("GRAFT_HOST", raising=False)

    settings = load_settings()

    assert settings == Settings(pricing_mode="local", graft_host=None)


def test_pricing_mode_defaults_to_remote(monkeypatch):
    monkeypatch.delenv("PRICING_MODE", raising=False)
    monkeypatch.delenv("GRAFT_HOST", raising=False)

    settings = load_settings()

    assert settings.pricing_mode == "remote"


def test_pricing_mode_normalised_to_lowercase(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "LOCAL")
    monkeypatch.delenv("GRAFT_HOST", raising=False)

    settings = load_settings()

    assert settings.pricing_mode == "local"


def test_invalid_pricing_mode_raises(monkeypatch):
    monkeypatch.setenv("PRICING_MODE", "cloud")

    with pytest.raises(ValueError, match="Invalid PRICING_MODE"):
        load_settings()

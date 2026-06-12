from order_service.config.settings import Settings, load_settings


def test_graft_host_read_from_env(monkeypatch):
    monkeypatch.setenv("GRAFT_HOST", "ws://localhost/ws")

    settings = load_settings()

    assert settings == Settings(graft_host="ws://localhost/ws")


def test_graft_host_defaults_to_none(monkeypatch):
    monkeypatch.delenv("GRAFT_HOST", raising=False)

    settings = load_settings()

    assert settings == Settings(graft_host=None)

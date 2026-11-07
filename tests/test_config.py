"""Tests de la configuration."""

from pathlib import Path

from immo_price.config import Settings, get_settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.model_path == Path("models/model.joblib")
    assert settings.data_dir == Path("data")
    assert settings.log_level == "INFO"


def test_env_variables_override_defaults(monkeypatch) -> None:
    monkeypatch.setenv("IMMO_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("IMMO_API_KEY", "secret-de-test")
    settings = Settings(_env_file=None)
    assert settings.log_level == "DEBUG"
    assert settings.api_key == "secret-de-test"


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()
    assert get_settings() is get_settings()
    get_settings.cache_clear()

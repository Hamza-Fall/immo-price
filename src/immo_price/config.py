"""Configuration de l'application via variables d'environnement."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres lus depuis l'environnement ou le fichier .env."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="IMMO_", extra="ignore"
    )

    api_key: str = ""
    model_path: Path = Path("models/model.joblib")
    data_dir: Path = Path("data")
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Retourne les paramètres de l'application (mis en cache)."""
    return Settings()

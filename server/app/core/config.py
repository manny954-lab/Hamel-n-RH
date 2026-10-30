"""Configuración central del servidor mediante variables de entorno.

Nunca se almacenan credenciales en el código fuente. Los valores se leen del
entorno o del archivo .env (solo desarrollo/local). En producción se inyectan
por el entorno del sistema o por un gestor de secretos.
"""

from pathlib import Path
from functools import lru_cache
from typing import List

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # Entorno
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Base de datos (por defecto SQLite: archivo local, sin servidor externo.
    # Funciona sin conexión y sin importar la red WiFi. Se puede sobrescribir con
    # DATABASE_URL=postgresql+... en .env si se desea usar PostgreSQL central.)
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="hamelin_rh", alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    database_url: str = Field(
        default="sqlite:///./hamelin_rh.db",
        alias="DATABASE_URL",
    )

    # Servidor
    backend_host: str = Field(default="127.0.0.1", alias="BACKEND_HOST")
    backend_port: int = Field(default=8001, alias="BACKEND_PORT")
    backend_reload: bool = Field(default=False, alias="BACKEND_RELOAD")

    # URL que usa el cliente de escritorio para conectar a la API (localhost =
    # funciona sin importar la red WiFi ni si hay conexión a Internet).
    client_api_url: str = Field(default="http://127.0.0.1:8001", alias="CLIENT_API_URL")

    # Seguridad
    secret_key: str = Field(default="cambiar_en_produccion", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    session_idle_timeout_minutes: int = Field(default=60, alias="SESSION_IDLE_TIMEOUT_MINUTES")

    login_max_intentos: int = Field(default=5, alias="LOGIN_MAX_INTENTOS")
    login_bloqueo_minutos: int = Field(default=15, alias="LOGIN_BLOQUEO_MINUTOS")

    # Almacenamiento de adjuntos
    adjuntos_dir: str = Field(default="./data/adjuntos", alias="ADJUNTOS_DIR")

    @validator("secret_key")
    def _validar_secret_key(cls, v: str, values) -> str:
        if not v:
            raise ValueError("SECRET_KEY no puede estar vacía")
        entorno = values.get("environment")
        if v == "cambiar_en_produccion" and entorno == "production":
            raise ValueError("SECRET_KEY debe ser cambiada antes de usar en producción")
        return v

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración en caché (singleton)."""
    return Settings()


settings = get_settings()

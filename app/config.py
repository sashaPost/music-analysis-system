from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os
import logging

from app.constants.routes import API_PREFIX

__all__ = ["settings"]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ENV = os.getenv("ENV", "dev")
ENV_FILE = f".env.{ENV}"
logger.debug(f"Loading environment config from: {ENV_FILE}")


class Settings(BaseSettings):
    # --- Meta ---
    environment: str = ENV

    # --- Database ---
    database_url: str = Field(..., description="PostgreSQL connection URI")
    redis_url: str = Field(..., description="Redis connection URI")

    # --- API ---
    # api_v1_prefix: str = "/api/v1"
    api_v1_prefix: str = API_PREFIX
    debug: bool = False
    secret_key: str = Field(..., min_length=16)
    algorithm: str = "HS256"

    # --- External APIs ---
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    spotify_redirect_uri: Optional[str] = None

    # --- ML / Model Config ---
    model_path: str = "./data/models/"
    batch_size: int = 32
    epochs: int = 100

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        protected_namespaces=("settings_",)
    )


settings = Settings()   # type: ignore[call-arg]
logger.debug("Loaded config:")
logger.debug(settings.model_dump())

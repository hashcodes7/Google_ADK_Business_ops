
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Business Operations Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # E-commerce backend
    ECOMMERCE_API_URL: str

    # Google ADK / Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", f"environments/.env.{os.getenv('APP_ENV', 'dev')}"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

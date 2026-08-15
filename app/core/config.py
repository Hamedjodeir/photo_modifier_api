from functools import lru_cache

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """
    Application configuration.

    Values can be supplied through environment variables.
    """

    app_name: str = "Photo Modifier API"

    app_version: str = "0.1.0"

    environment: str = "development"

    debug: bool = False

    max_upload_size: int = Field(
        default=25 * 1024 * 1024,
        gt=0,
    )

    max_image_pixels: int = Field(
        default=100_000_000,
        gt=0,
    )

    max_animation_frames: int = Field(
        default=500,
        gt=0,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings.

    Caching ensures that configuration is loaded once per
    process rather than being re-read on every request.
    """

    return Settings()


settings = get_settings()
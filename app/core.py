from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "PocketSmart AI"

    secret_key: str = "change-me"

    database_url: str = "sqlite:///./pocketsmart.db"

    gemini_api_key: str | None = None

    gemini_model: str = "gemini-2.5-flash"

    access_token_expire_minutes: int = 60

    session_cookie_name: str = "pocketsmart_session"

    allowed_origins: str = (
        "http://127.0.0.1:8000,"
        "http://localhost:8000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def origins(self):
        return [
            x.strip()
            for x in self.allowed_origins.split(",")
            if x.strip()
        ]


@lru_cache
def settings():
    return Settings()
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    database_url: str = "sqlite:///./transparency.db"

    # Set to false on networks with a TLS-intercepting proxy (self-signed CA).
    verify_ssl: bool = True

    # Optional news API keys for the (pluggable) news collectors.
    gnews_api_key: str = ""
    newsapi_key: str = ""

    # Default lookback window for collectors that support it.
    ingest_timespan: str = "12m"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    # Backup LLM configuration (fallback if primary fails)
    llm_backup_key: str = ""
    llm_backup_base_url: str = ""
    llm_backup_model: str = ""

    database_url: str = "sqlite:///./transparency.db"

    # Set to false on networks with a TLS-intercepting proxy (self-signed CA).
    verify_ssl: bool = True

    # Optional news API keys for the (pluggable) news collectors.
    gnews_api_key: str = ""
    newsapi_key: str = ""
    newsdata_api_key: str = ""
    mediastack_api_key: str = ""
    currents_api_key: str = ""

    # Default lookback window for collectors that support it.
    ingest_timespan: str = "12m"

    # Max items taken from each individual news source (bounds LLM cost).
    max_items_per_source: int = 60

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key.strip())

    @property
    def llm_backup_enabled(self) -> bool:
        return bool(self.llm_backup_key.strip())

    @property
    def is_postgresql(self) -> bool:
        return self.database_url.startswith("postgresql://")


@lru_cache
def get_settings() -> Settings:
    return Settings()

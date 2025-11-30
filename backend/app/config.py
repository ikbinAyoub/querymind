"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "SQL-RAG System"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # LLM Configuration
    llm_provider: Literal["openai", "azure_openai"] = "openai"
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4"
    
    # Azure OpenAI Configuration
    azure_openai_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    schema_cache_ttl: int = 3600  # 1 hour

    # Database Query Settings
    query_timeout: int = 30  # seconds
    max_result_rows: int = 1000

    # Security
    allowed_sql_keywords: list[str] = Field(
        default_factory=lambda: ["SELECT", "WITH", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY", "LIMIT", "OFFSET", "HAVING", "UNION", "INTERSECT", "EXCEPT"]
    )
    forbidden_sql_keywords: list[str] = Field(
        default_factory=lambda: ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"]
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

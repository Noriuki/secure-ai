from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Secure AI API"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    database_url: str = "postgresql+psycopg://secure_ai:secure_ai@localhost:5435/secure_ai"

    aws_region: str = "us-east-1"
    s3_bucket: str = ""
    bedrock_knowledge_base_id: str = ""
    bedrock_data_source_id: str = ""
    presidio_analyzer_url: str = "http://localhost:5003"
    presidio_timeout_seconds: float = 15.0


@lru_cache
def get_settings() -> Settings:
    return Settings()

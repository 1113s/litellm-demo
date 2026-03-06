from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "litellm-openrouter-demo"
    env: str = "dev"
    database_url: str = "postgresql+psycopg://litellm:litellm@postgres:5432/litellm_demo"
    redis_url: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

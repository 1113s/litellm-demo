from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "litellm-openrouter-demo"
    env: str = "dev"

    database_url: str = Field(
        default="postgresql+psycopg://litellm:litellm@postgres:5432/litellm_demo",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    litellm_base_url: str = Field(default="http://litellm:4000", alias="LITELLM_BASE_URL")
    litellm_admin_key: str = Field(default="", alias="LITELLM_MASTER_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

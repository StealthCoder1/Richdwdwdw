from typing import Any

from pydantic_settings import BaseSettings

from app.constants import Environment


class Config(BaseSettings):
    ENVIRONMENT: Environment = Environment.LOCAL

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def SQLALCHEMY_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Config()

app_configs: dict[str, Any] = {"title": "RichSMM"}

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs

from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 5  # minutes

    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 7  # 7 day
    SECURE_COOKIES: bool = False
    ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = "allow"
        case_sensitive = True


auth_config = AuthConfig()

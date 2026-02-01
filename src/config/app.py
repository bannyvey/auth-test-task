from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):


    jwt_secret_key: SecretStr
    jwt_algorithm: str
    jwt_issuer: str
    jwt_audience: str

    access_token_expire_minutes: int = 1
    refresh_token_expire_days: int = 7
    cookie_expire_one_min: int = 60

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
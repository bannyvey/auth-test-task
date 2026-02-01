from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from src.config.app import AppConfig
from src.config.database import DatabaseConfig
from src.config.logging_config import LoggingConfig
from src.config.redis import RedisConfig

# src/config/settings.py


class Settings(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    app: AppConfig = AppConfig()
    logging: LoggingConfig = LoggingConfig()
    redis_config: RedisConfig = RedisConfig()

@lru_cache
def get_settings() -> Settings:
    return Settings()
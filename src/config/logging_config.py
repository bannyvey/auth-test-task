import logging.config
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

# src/config/logging_config.py


class LoggingConfig(BaseSettings):
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def get_config(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": self.log_format
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "detailed",
                    "level": "DEBUG",
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "src.services": {"level": "DEBUG"},
                "src.repositories": {"level": "INFO"},
                "src.api": {"level": "DEBUG"},
            },
        }

    def setup(self):
        logging.config.dictConfig(self.get_config())

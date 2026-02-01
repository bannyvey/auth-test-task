from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


#src/config/database.py

class DatabaseConfig(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_host_port: int
    postgres_password: str
    postgres_user: str
    postgres_db: str


    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @computed_field
    @property
    def get_database(self) -> str:
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
                f"{self.postgres_host}:{self.postgres_host_port}/{self.postgres_db}"
                )
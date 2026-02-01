from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):

    redis_host: str
    redis_port: int
    redis_host_port: int
    redis_password: str
    redis_cache_ttl: str = 300


    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # @property
    # def redis_host(self):
    #     return f'redis://{self.redis_password}@{self.redis_host}:{self.redis_port}'
import logging
from redis.asyncio import Redis, ConnectionPool

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class RedisClient:
    _redis: Redis = None
    _pool: ConnectionPool = None

    @classmethod
    async def init_pool(cls) -> None:
        """открытие"""
        setting = get_settings().redis_config
        cls._pool = ConnectionPool(
            host=setting.redis_host,
            port=setting.redis_host_port,
            decode_responses=True,
            max_connections=40,

            socket_connect_timeout=5,  # сколько ждать подключения
            socket_timeout=10,  # сколько ждать ответа на команду
            socket_keepalive=True,  # полезно в долгоживущих приложениях
            retry_on_timeout=True,  # переподключаться при таймаутах
        )
        cls._redis = Redis(connection_pool=cls._pool)
        await cls._redis.ping()
        logger.info("Redis connection pool initialized successfully")

    @classmethod
    async def close_pool(cls) -> None:
        """закрытие"""
        try:
            if cls._redis:
                await cls._redis.aclose()
                cls._redis = None
                logger.info("Redis client closed")

            if cls._pool:
                await cls._pool.disconnect()
                cls._pool = None
                logger.info("Redis pool disconnected")

        except Exception as e:
            logger.error(f"Error closing Redis pool: {e}")

    @classmethod
    def get_client(cls) -> Redis:
        """Для ДИАЙ"""
        if cls._redis is None:
            raise RuntimeError(
                "Redis not initialized. Call RedisClient.init_pool() first"
            )
        return cls._redis




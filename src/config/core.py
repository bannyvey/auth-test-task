from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from src.config.settings import get_settings

#src/config/core.py


engine = create_async_engine(get_settings().database.get_database, echo=False, pool_size=5, max_overflow=10 )


local_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
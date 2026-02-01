from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.Models.User import User
from src.clients.redis import RedisClient
from src.config.core import local_session
from src.security.jwt_service import JwtService
from src.services.admin_service import AdminService
from src.services.auth_service import AuthService
from src.repositories.user_repository import UserRepository
from src.exceptions.custom_exceptions import (
    InvalidCredentialsException
)

logger = logging.getLogger(__name__)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения сессии базы данных"""
    async with local_session() as session:
        try:
            yield session
            await session.commit()
        except HTTPException:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_redis() -> Redis:
    """FastAPI dependency для получения Redis клиента"""
    return RedisClient.get_client()


def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    """Factory для создания AuthRepository с сессией"""
    return UserRepository(session=session)


def get_jwt_service(

) -> JwtService:
    """Dependency для JWT сервиса"""
    return JwtService()


async def get_auth_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)],
        jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
        redis: Annotated[Redis, Depends(get_redis)],
) -> AuthService:
    """Dependency для AuthService"""
    return AuthService(repository, jwt_service, redis)


async def get_admin_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AdminService:
    """Dependency для AdminService"""
    return AdminService(repository)


async def get_current_user(
        request: Request,
        repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Получить текущего пользователя по токену"""
    token = request.cookies.get("access_token")
    if not token:
        raise InvalidCredentialsException(detail="Not authenticated")
    payload = JwtService.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise InvalidCredentialsException(detail="Invalid token")
    try:
        user_id = int(payload["sub"])
    except (ValueError, KeyError):
        raise InvalidCredentialsException(detail="Invalid token")
    user = await repository.find_by_id(user_id)
    if not user or not user.is_active:
        raise InvalidCredentialsException(detail="User not found or inactive")
    return user


async def require_admin(
        current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Проверить что текущий пользователь админ"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

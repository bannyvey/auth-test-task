import logging
from typing import List

from fastapi import HTTPException, Request, Response
from redis.asyncio import Redis

from src.config.settings import get_settings
from src.schemes.schemes import (
    Registration, LoginRequest, UpdateUser, UserResponse
)
from src.exceptions.custom_exceptions import (
    NotFoundException, AlreadyExistsException, ServiceError, InvalidCredentialsException
)
from src.security.jwt_service import JwtService
from src.repositories.user_repository import UserRepository
from src.Models.User import User

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: UserRepository, jwt_service: JwtService, redis: Redis):
        self.repository = repository
        self.jwt_service = jwt_service
        self.redis = redis

    def _set_cookie(self, response: Response, key: str, value: str, max_age) -> None:
        response.set_cookie(
            key=key,
            value=value,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
            path="/",
        )
    async def login(self, data: LoginRequest, response: Response) -> UserResponse:
        """Вход по емайлу и паролю, возвращает пользователя"""
        user = await self.repository.find_one_or_none({"email": data.email})
        if not user:
            raise NotFoundException(detail="User not found by email")
        if not self.jwt_service.verify_password(data.password, user.hash_password):
            raise InvalidCredentialsException(detail="Wrong password")
        if not user.is_active:
            raise InvalidCredentialsException(detail="User account is disabled")
        access_token = self.jwt_service.create_access_token(user.id)
        refresh_token, refresh_ttl_sec = self.jwt_service.create_refresh_token(user.id)  # ← используй tuple

        redis_key = f"refresh:{refresh_token}"
        await self.redis.set(redis_key, str(user.id), ex=refresh_ttl_sec)

        # Куки access
        access_max_age_sec = get_settings().app.access_token_expire_minutes * 60
        self._set_cookie(response, "access_token", access_token, access_max_age_sec)

        # Куки refresh
        self._set_cookie(response, "refresh_token", refresh_token, refresh_ttl_sec)

        return UserResponse.model_validate(user)


    async def register(self, data: Registration, response) -> UserResponse:
        """Регистрация нового пользователя"""
        exist_user = await self.repository.find_one_or_none({"email": data.email})
        if exist_user:
            raise AlreadyExistsException(detail="Email already registered")
        hash_password = await self.jwt_service.hash_password(data.password)
        user_data = {
            "first_name": data.first_name,
            "last_name": data.last_name,
            "email": data.email,
            "hash_password": hash_password
        }
        new_user = await self.repository.add(user_data)

        access_token = self.jwt_service.create_access_token(new_user.id)
        refresh_token, refresh_ttl_sec = self.jwt_service.create_refresh_token(new_user.id)

        redis_key = f"refresh:{refresh_token}"
        await self.redis.set(redis_key, str(new_user.id), ex=refresh_ttl_sec)

        access_max_age_sec = get_settings().app.access_token_expire_minutes * 60
        self._set_cookie(response, "access_token", access_token, access_max_age_sec)

        self._set_cookie(response, "refresh_token", refresh_token, refresh_ttl_sec)

        return UserResponse.model_validate(new_user)
    async def get_me(self, user: User) -> UserResponse:
        """"""
        return UserResponse.model_validate(user)

    async def update_profile(self, user: User, data: UpdateUser) -> UserResponse:
        """Обновление профиля пользователя (частичное обновление)"""
        print("1")
        if data.email and data.email != user.email:
            existing = await self.repository.find_one_or_none({"email": data.email})
            if existing:
                raise AlreadyExistsException(detail="Email already in use")
        update_data = data.model_dump(exclude_none=True)
        print(update_data)
        if not update_data:
            raise NotFoundException("No data to update")
        update_user = await self.repository.update(user.id, update_data)
        updated_user = UserResponse.model_validate(update_user)
        return UserResponse.model_validate(updated_user)

    async def delete_user(self, user: User) -> dict:
        """Удаление пользователя (soft delete - устанавливаем is_active=False)"""
        await self.repository.update(user.id, {"is_active": False})
        return {"message": "User account deleted successfully"}

    async def refresh_token(self, request: Request, response: Response) -> UserResponse:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise InvalidCredentialsException("Нет refresh токена в cookie")

        redis_key = f"refresh:{refresh_token}"
        user_id_str = await self.redis.get(redis_key)
        print(user_id_str)
        if not user_id_str:
            raise InvalidCredentialsException("Refresh недействителен или истёк")

        try:
            user_id = int(user_id_str)
        except ValueError:
            await self.redis.delete(redis_key)
            raise InvalidCredentialsException("Повреждённые данные в Redis")

        user = await self.repository.find_by_id(user_id)
        if not user or not user.is_active:
            await self.redis.delete(redis_key)
            raise InvalidCredentialsException("Пользователь не найден / заблокирован")

        # Ротация
        await self.redis.delete(redis_key)

        new_access = self.jwt_service.create_access_token(user.id)
        new_refresh, new_ttl_sec = self.jwt_service.create_refresh_token(user.id)

        await self.redis.set(f"refresh:{new_refresh}", str(user.id), ex=new_ttl_sec)

        access_max_age_sec = get_settings().app.access_token_expire_minutes * 60
        self._set_cookie(response, "access_token", new_access, access_max_age_sec)
        self._set_cookie(response, "refresh_token", new_refresh, new_ttl_sec)

        return UserResponse.model_validate(user)
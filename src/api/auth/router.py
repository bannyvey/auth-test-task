from fastapi import APIRouter, Depends, status, Response, Request
from redis.asyncio import Redis

from src.Models.User import User
from src.schemes.schemes import Registration, UpdateUser, UserResponse, LoginRequest
from src.di.dependencies import get_auth_service, get_current_user, get_redis
from src.services.auth_service import AuthService

router = APIRouter(tags=["Auth Service"], prefix="/auth")


@router.post("/login", response_model=UserResponse)
async def login(
        request: LoginRequest,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(request, response)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        request: Registration,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service),
):
    """Регистрация нового пользователя"""
    return await auth_service.register(request, response)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    redis: Redis = Depends(get_redis)
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await redis.delete(f"refresh:{refresh_token}")

    response.delete_cookie("access_token", path="/", httponly=True, secure=True, samesite="lax")
    response.delete_cookie("refresh_token", path="/", httponly=True, secure=True, samesite="lax")

    return {"message": "Вы вышли из аккаунта"}


@router.get("/me", response_model=UserResponse, response_model_exclude_none=True)
async def get_me(
        current_user: User = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
):
    """Получить информацию о текущем пользователе"""
    return await auth_service.get_me(current_user)


@router.put("/profile", response_model=UserResponse, response_model_exclude_none=True)
async def update_profile(
        request: UpdateUser,
        current_user: User = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
):
    """Обновление профиля текущего пользователя (частичное обновление поддерживается)"""
    return await auth_service.update_profile(current_user, request)


@router.delete("/profile")
async def delete_user(
        current_user: User = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
):
    """Удаление аккаунта пользователя (soft delete: is_active=False)"""
    return await auth_service.delete_user(current_user)


@router.post("/refresh", response_model=UserResponse)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.refresh_token(request, response)

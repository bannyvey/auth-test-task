from typing import Literal
from fastapi import Depends, Query, APIRouter
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.di.dependencies import get_session, get_admin_service
from src.schemes.pagination_filter import PaginationFilter
from src.schemes.schemes import UserSchema as UserSchema, UserResponse
from src.services.admin_service import AdminService

router = APIRouter(tags=["Admins"], prefix="/admin")


@router.get("/users", response_model=Page[UserSchema])
async def get_all_users(
        order_by: str = Query("id"),
        direction: Literal["desc", "asc"] = Query("desc", description="Направление сортировки"),
        size: int = Query(default=None, description="Кол-во объектов"),
        page: int = Query(default=None, description='Номер страницы'),
        email: str = Query(default=None, description="Поиск по email"),
        session: AsyncSession = Depends(get_session),
):
    """Получить список всех пользователей (доступно только для админов)"""
    filter_params = PaginationFilter(
        order_by=order_by,
        order_by_direction=direction,
        size=size,
        page=page,
        extra={
            "email": email
        }
    )
    return await UserSchema.paginate(session, filter_params)


@router.put("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
        user_id: int,
        role: Literal["admin", "user"] = Query("admin"),
        admin_service: AdminService = Depends(get_admin_service),
):
    """Смена роли админом"""
    return await admin_service.updating_role(user_id, role)

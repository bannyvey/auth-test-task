from typing import ClassVar, Self
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from src.Models.base import Base
from src.schemes.pagination_filter import PaginationFilter


class PaginationMixin:
    model: ClassVar[type[Base]]

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        filter_params: PaginationFilter | None = None,

    ) -> Page[Self]:

        """Получить пагинированный список объектов"""
        if filter_params is None:
            filter_params = PaginationFilter(page=0, size=1)
        try:
            statement = cls.model.get_filter_statement(filter_params)
        except Exception:
            raise
        return await paginate(session, statement)
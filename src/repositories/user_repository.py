from typing import List

from sqlalchemy import select, update, ScalarResult, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.Models.User import User


class UserRepository:
    """Repository для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User

    async def find_by_id(self, _id: int):
        """Найти пользователя по ID"""
        entity = await self.session.scalar(select(self.model).where(self.model.id == _id))
        return entity

    async def find_one_or_none(self, _filter: dict):
        """Найти одного пользователя по фильтру или вернуть None"""
        entity = await self.session.scalar(select(self.model).filter_by(**_filter))
        return entity

    async def add(self, entity: dict) -> User:
        """Добавить нового пользователя"""
        user = self.model(**entity)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, _id: int, data: dict) -> User:
        """Обновить пользователя по ID (частичное обновление)"""
        await self.session.execute(update(self.model).where(self.model.id == _id).values(**data))
        refreshed = await self.session.get(self.model, _id)
        if refreshed is None:
            raise ValueError("User not found after update")
        return refreshed

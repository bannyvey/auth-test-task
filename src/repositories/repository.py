from abc import ABC
from typing import TypeVar, Generic, Type
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class Repository(Generic[T]):

    def __init__(self, model: T, session: AsyncSession | None = None):
        self.session = session
        self.model = model

    async def find_by_id(self, _id: int):
        entity = await self.session.scalar(select(self.model).where(self.model.id == _id))
        return entity

    async def find_one_or_none(self, _filter: dict):
        entity = await self.session.scalar(select(self.model).filter_by(**_filter))
        return entity

    async def find_all(self, _filter: dict = None):
        # # ADDED: поддержка пустого фильтра для получения всех записей
        if _filter is None:
            entity = await self.session.scalars(select(self.model))
        else:
            entity = await self.session.scalars(select(self.model).filter_by(**_filter))
        return entity.all()

    async def add(self, entity: T):
        entity = self.model(**entity)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, _id: int, _dict: dict):
        """Обновляет поля которые были переданы (unset значения игнорируются)"""
        update_dict = {k: v for k, v in _dict.items() if v is not None}
        if not update_dict:
            return await self.find_by_id(_id)

        await self.session.execute(
            update(self.model).where(self.model.id == _id).values(**update_dict)
        )
        await self.session.flush()
        return await self.find_by_id(_id)

    async def soft_delete(self, entity: Type[T]):
        entity.is_active = False

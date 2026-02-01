from sqlalchemy import select, Select
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    @classmethod
    def get_filter_statement(cls, kwargs) -> Select:
        """Создать SQL запрос с фильтрами (базовая реализация)"""
        statement = select(cls)
        # Сортировка
        if kwargs.order_by:
            field = getattr(cls, kwargs.order_by)
            if kwargs.order_by_direction == "desc":
                statement = statement.order_by(field.desc())
            else:
                statement = statement.order_by(field.asc())
        # Фильтры

        if kwargs.extra:
            cond_list = cls.get_cond_list(**kwargs.extra)

            if cond_list:
                statement = statement.where(*cond_list)
        # Пагинация
        if kwargs.page is not None:
            statement = statement.offset(kwargs.page)
        if kwargs.size is not None:
            statement = statement.limit(kwargs.size)
        return statement

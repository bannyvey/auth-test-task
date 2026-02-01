from typing import Literal, NamedTuple
from pydantic import Field


class PaginationFilter(NamedTuple):
    page: int | None = Field(default=None, description="Номер страницы")
    size: int | None = Field(default=None, description="Размер объектов на странице")
    order_by: str | None = Field(default="id", description="Поле для сортировки")
    order_by_direction: Literal["desc", "asc"] = Field(default="desc", description="Направление сортировки")
    extra: dict | None = Field(default=None, description="Дополнительные фильтры")
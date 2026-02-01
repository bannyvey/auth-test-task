from datetime import datetime
from pydantic import BaseModel, model_validator, ConfigDict, EmailStr, Field
from typing import Optional, ClassVar

from src.Models.User import User
from src.schemes.mixin import PaginationMixin


class Base(BaseModel):
    model: ClassVar[type[User]] = User
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class UserSchema(Base, PaginationMixin):

    """Для пагинации"""
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    created_at: datetime


class LoginRequest(BaseModel):

    """Мхема для входа"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class Registration(BaseModel):
    """Схема для регистрации"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.password2:
            raise ValueError("Passwords don't match")
        return self


class UpdateUser(BaseModel):
    """Схема для обновления профиля"""
    first_name: Optional[str] = Field(default="Ввести имя или null", min_length=1, max_length=50)
    last_name: Optional[str] = Field(default="Ввести фамилию или null", min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(default="Ввести email или null", min_length=1, max_length=50)


class UserResponse(BaseModel):
    """Ответ с информацией о пользователе"""
    id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool
    role: str
    refresh_token_hash: str | None = None


    model_config = ConfigDict(from_attributes=True)

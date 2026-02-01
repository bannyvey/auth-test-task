from fastapi import HTTPException, status


class ServiceError(Exception):
    """
    Базовое исключение для бизнес-логики сервисов.
    Используется для ошибок, которые НЕ являются HTTPException
    """

    def __init__(
            self,
            message: str,
            *,
            status_code: int = 400,
            public_detail: str | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.public_detail = public_detail or message
        super().__init__(message)


class NotFoundException(HTTPException):
    """Исключение когда сущность не найдена (404)"""

    def __init__(self, detail: str = "Entity not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )



class InvalidCredentialsException(HTTPException):
    """неверный логин или пароль"""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AlreadyExistsException(HTTPException):
    """Исключение когда сущность уже существует"""

    def __init__(self, detail: str = "Entity already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class RequestValidationException(HTTPException):
    """Исключение для кастомной валидации (400)"""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )





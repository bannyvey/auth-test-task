from src.exceptions.custom_exceptions import AlreadyExistsException
from src.repositories.user_repository import UserRepository
from src.schemes.schemes import UserResponse


class AdminService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def updating_role(self, user_id: int, role: str) -> UserResponse:
        user = await self.repository.find_by_id(user_id)
        if not user:
            raise AlreadyExistsException("User not fount by id")
        updated_user = await self.repository.update(user.id, {"role": role})
        return UserResponse.model_validate(updated_user)

from abc import ABC, abstractmethod
from typing import Optional, Any
from app.domain.dtos.user_dto import UserResponseDTO
from app.domain.enums import UserStatus


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        portrait: str | None = None,
        status: UserStatus | None = None,
    ) -> UserResponseDTO:
        raise NotImplementedError
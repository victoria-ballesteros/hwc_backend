from app.adapters.database.dependencies import get_role_repository
from app.domain.dtos.user_dto import UserDTO
from fastapi import Depends, HTTPException, status # type: ignore
from typing import List
from app.adapters.routing.utils.context import user_context


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserDTO, repo=Depends(get_role_repository)) -> None:
        role_id = user.role_id


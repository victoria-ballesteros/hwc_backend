from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.adapters.database.postgres.repositories.user_repository import UserRepository
from app.adapters.database.dependencies import (
    get_register_user_handler,
    get_login_user_handler,
    get_refresh_access_token_pro_handler,
    get_signout_pro_handler,
    get_current_user_payload,
    get_db,
)
from app.adapters.routing.utils.decorators import format_response
from app.adapters.routing.utils.response import ResultSchema
from app.domain.dtos.user_dto import (
    RegisterUserInputDTO,
    UserResponseDTO,
    LoginInputDTO,
    LoginResponseDTO,
    RefreshTokenInputDTO,
    RefreshTokenResponseDTO,
    SignOutInputDTO,
    SignOutResponseDTO,
)
from app.domain.exceptions.base_exceptions import UnauthorizedException
from app.ports.driving.handler_interface import HandlerInterface

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=ResultSchema[UserResponseDTO])
@format_response
def register_user(
    data: RegisterUserInputDTO,
    use_case: HandlerInterface = Depends(get_register_user_handler),
) -> Any:
    return use_case.execute(data)


@router.post("/login", response_model=ResultSchema[LoginResponseDTO])
@format_response
def login(
    data: LoginInputDTO,
    use_case: HandlerInterface = Depends(get_login_user_handler),
) -> Any:
    return use_case.execute(data)



@router.post("/refresh", response_model=ResultSchema[RefreshTokenResponseDTO])
@format_response
def refresh(
    data: RefreshTokenInputDTO,
    use_case: HandlerInterface = Depends(get_refresh_access_token_pro_handler),
) -> Any:
    return use_case.execute(data)


@router.post("/signout", response_model=ResultSchema[SignOutResponseDTO])
@format_response
def signout(
    data: SignOutInputDTO,
    use_case: HandlerInterface = Depends(get_signout_pro_handler),
) -> Any:
    return use_case.execute(data)


@router.get("/me", response_model=ResultSchema[UserResponseDTO])
@format_response
def me(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
) -> Any:
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token inválido: falta sub")

    user = UserRepository(db).get_by_id(int(user_id))  # <-- necesitas este método
    if not user:
        raise UnauthorizedException("Usuario no existe o sesión inválida")

    return UserResponseDTO.from_orm(user)


@router.get("/verify", response_model=ResultSchema[dict])
@format_response
def verify_email(
    token: str = Query(..., min_length=10),
    db: Session = Depends(get_db),
) -> Any:
    user = UserRepository(db).get_by_verification_token(token)
    if not user or not user.verification_expires_at:
        raise UnauthorizedException("Invalid or expired verification token")

    now = datetime.now(timezone.utc)
    expires_at = user.verification_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise UnauthorizedException("Invalid or expired verification token")

    user.is_verified = True
    user.verification_token = None
    user.verification_expires_at = None

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Email verified successfully"}
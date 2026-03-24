from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.database.dependencies import (
    get_create_team_handler,
    get_current_user_payload,
    get_delete_team_handler,
    get_delete_team_invitation_handler,
    get_send_team_invitations_handler,
)
from app.adapters.routing.utils.decorators import format_response
from app.adapters.routing.utils.response import ResultSchema
from app.domain.dtos.team_dto import (
    CreateTeamInputDTO,
    CreateTeamResponseDTO,
    DeleteTeamInvitationResponseDTO,
    DeleteTeamResponseDTO,
    SendTeamInvitationsInputDTO,
    SendTeamInvitationsResponseDTO,
)
from app.domain.exceptions.base_exceptions import UnauthorizedException
from app.ports.driving.handler_interface import HandlerInterface

router = APIRouter(prefix="/teams", tags=["teams"])


def _get_current_user_id(payload: dict) -> int:
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token: missing sub")
    return int(user_id)


@router.post("", status_code=201, response_model=ResultSchema[CreateTeamResponseDTO])
@format_response
def create_team(
    data: CreateTeamInputDTO,
    payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_create_team_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(payload), data)


@router.post(
    "/invitations",
    response_model=ResultSchema[SendTeamInvitationsResponseDTO],
)
@format_response
def send_team_invitations(
    data: SendTeamInvitationsInputDTO,
    payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_send_team_invitations_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(payload), data)


@router.delete(
    "/invitations/{team_request_id}",
    response_model=ResultSchema[DeleteTeamInvitationResponseDTO],
)
@format_response
def delete_team_invitation(
    team_request_id: int,
    payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_delete_team_invitation_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(payload), team_request_id)


@router.delete("/{team_id}", response_model=ResultSchema[DeleteTeamResponseDTO])
@format_response
def delete_team(
    team_id: int,
    payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_delete_team_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(payload), team_id)

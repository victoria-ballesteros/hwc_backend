from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.database.dependencies import (
    get_accept_team_invitation_handler,
    get_create_team_handler,
    get_current_user_payload,
    get_delete_team_handler,
    get_delete_team_invitation_handler,
    get_list_my_team_invitations_handler,
    get_list_teams_handler,
    get_send_team_invitations_handler,
    get_team_detail_handler,
)
from app.adapters.routing.utils.decorators import format_response
from app.adapters.routing.utils.response import ResultSchema
from app.domain.dtos.team_dto import (
    AcceptTeamInvitationResponseDTO,
    CreateTeamInputDTO,
    CreateTeamResponseDTO,
    DeleteTeamInvitationResponseDTO,
    DeleteTeamResponseDTO,
    GetTeamDetailResponseDTO,
    ListMyTeamInvitationsResponseDTO,
    ListTeamsResponseDTO,
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


@router.get("", response_model=ResultSchema[ListTeamsResponseDTO])
@format_response
def list_teams(
    _payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_list_teams_handler),
) -> Any:
    return use_case.execute()


@router.get("/{team_id}", response_model=ResultSchema[GetTeamDetailResponseDTO])
@format_response
def get_team_detail(
    team_id: int,
    _payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_team_detail_handler),
) -> Any:
    return use_case.execute(team_id)


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


@router.get(
    "/invitations/me",
    response_model=ResultSchema[ListMyTeamInvitationsResponseDTO],
)
@format_response
def list_my_team_invitations(
    payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_list_my_team_invitations_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(payload))


@router.post(
    "/invitations/{team_request_id}/accept",
    response_model=ResultSchema[AcceptTeamInvitationResponseDTO],
)
@format_response
def accept_team_invitation(
    team_request_id: int,
    payload: dict = Depends(get_current_user_payload),
    use_case: HandlerInterface = Depends(get_accept_team_invitation_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(payload), team_request_id)


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

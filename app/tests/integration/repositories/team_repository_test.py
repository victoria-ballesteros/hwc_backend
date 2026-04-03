from app.adapters.database.postgres.connection import SessionLocal
from app.adapters.database.postgres.models.user_model import User
from app.domain.dtos.team_dto import TeamResponseDTO
from app.domain.enums import TeamRequestStatus
from app.domain.exceptions.base_exceptions import TeamNotFoundException
from app.ports.driving.team_interface import TeamQueryInterface
import pytest # type: ignore
from app.adapters.database.postgres.repositories.team_repository import TeamRepository


@pytest.fixture
def db_session():
    return SessionLocal()

@pytest.fixture
def repo(db_session) -> TeamQueryInterface:
    return TeamRepository(db_session)

def test_get_active_users_from_migration(repo: TeamQueryInterface) -> None:
    active_users = repo.get_active_users()
    emails = [u.email for u in active_users]

    assert "daniel.bautista@unet.edu.ve" in emails
    assert "douglas.moreno@unet.edu.ve" in emails
    assert "maria.ballesteros@unet.edu.ve" not in emails

def test_get_user_team_not_found_real_user(repo, db_session) -> None:
    user = db_session.query(User).filter_by(email="maria.ballesteros@unet.edu.ve").first()

    assert user is not None, "El usuario de la migración no existe en la BD"

    with pytest.raises(TeamNotFoundException):
        repo.get_user_team(str(user.id))


def test_get_user_team_info_is_correct(repo, db_session):
    user = db_session.query(User).filter_by(email="daniel.bautista@unet.edu.ve").first()
    assert user is not None, "La migración no cargó al usuario Daniel"

    response = repo.get_user_team(str(user.id))

    assert isinstance(response, TeamResponseDTO)
    assert response.team_name == "UNET Cyber-Warriors"
    assert response.edition_name == "First Edition 2026"

    assert len(response.accepted_members) > 0
    member = response.accepted_members[0]
    assert member.email == "daniel.bautista@unet.edu.ve"
    assert member.username == "dbautista"
    assert member.status == TeamRequestStatus.ACCEPTED.name

    assert len(response.pending_members) == 0
    assert len(response.deleted_members) == 0


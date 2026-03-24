from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.adapters.database.postgres.models.category_model import Category
from app.adapters.database.postgres.models.edition_model import Edition
from app.adapters.database.postgres.models.team_model import Team
from app.adapters.database.postgres.models.user_model import (
    User,
    team_request_association,
    user_team_association,
)
from app.domain.dtos.team_dto import TeamRequestDTO, TeamResponseDTO
from app.domain.dtos.user_dto import UserDTO
from app.domain.enums import TeamRequestStatus
from app.domain.exceptions.base_exceptions import RecordNotFoundException
from app.ports.driven.database.postgres.team_repository_abc import (
    TeamRepositoryInterface,
)


class TeamRepository(TeamRepositoryInterface):
    def __init__(self, db: Session) -> None:
        self.db = db

    def category_exists(self, category_id: int) -> bool:
        return (
            self.db.query(Category).filter(Category.id == category_id).first()
            is not None
        )

    def get_latest_available_edition_id(self, current_date: datetime) -> int | None:
        edition = (
            self.db.query(Edition)
            .filter(Edition.end_date >= current_date)
            .order_by(Edition.id.desc())
            .first()
        )
        return edition.id if edition else None

    def get_user_by_id(self, user_id: int) -> UserDTO | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        return UserDTO.from_orm(user) if user else None

    def get_users_by_usernames(self, usernames: list[str]) -> list[UserDTO]:
        if not usernames:
            return []

        normalized_usernames = [username.strip().lower() for username in usernames]
        users = (
            self.db.query(User)
            .filter(func.lower(User.username).in_(normalized_usernames))
            .all()
        )
        return [UserDTO.from_orm(user) for user in users]

    def user_has_team(self, user_id: int) -> bool:
        result = self.db.execute(
            select(user_team_association.c.user_id).where(
                user_team_association.c.user_id == user_id
            )
        ).first()
        return result is not None

    def get_team_by_leader_id(self, leader_id: int) -> TeamResponseDTO | None:
        team = (
            self.db.query(Team)
            .filter(Team.assigned_evaluator_id == leader_id)
            .order_by(Team.id.desc())
            .first()
        )
        return TeamResponseDTO.from_orm(team) if team else None

    def get_team_by_id(self, team_id: int) -> TeamResponseDTO | None:
        team = self.db.query(Team).filter(Team.id == team_id).first()
        return TeamResponseDTO.from_orm(team) if team else None

    def create_team(
        self,
        name: str,
        edition_id: int,
        category_id: int,
        leader_id: int,
    ) -> TeamResponseDTO:
        team = Team(
            name=name,
            logo=None,
            score=None,
            standing_position=None,
            cloud_repo_link=None,
            edition_id=edition_id,
            category_id=category_id,
            evaluation_id=None,
            assigned_evaluator_id=leader_id,
        )

        try:
            self.db.add(team)
            self.db.flush()

            self.db.execute(
                user_team_association.insert().values(
                    user_id=leader_id,
                    team_id=team.id,
                )
            )

            self.db.commit()
            self.db.refresh(team)
            return TeamResponseDTO.from_orm(team)
        except Exception:
            self.db.rollback()
            raise

    def get_pending_request_receiver_ids(
        self,
        team_id: int,
        receiver_user_ids: list[int],
    ) -> set[int]:
        if not receiver_user_ids:
            return set()

        rows = self.db.execute(
            select(team_request_association.c.receiver_user_id).where(
                team_request_association.c.team_id == team_id,
                team_request_association.c.receiver_user_id.in_(receiver_user_ids),
                team_request_association.c.status == TeamRequestStatus.PENDING,
            )
        ).all()

        return {int(row[0]) for row in rows}

    def create_team_requests(
        self,
        team_id: int,
        sender_user_id: int,
        receiver_user_ids: list[int],
    ) -> list[TeamRequestDTO]:
        if not receiver_user_ids:
            return []

        try:
            rows = []
            for receiver_user_id in receiver_user_ids:
                row = self.db.execute(
                    team_request_association.insert()
                    .values(
                        team_id=team_id,
                        sender_user_id=sender_user_id,
                        receiver_user_id=receiver_user_id,
                        status=TeamRequestStatus.PENDING,
                    )
                    .returning(
                        team_request_association.c.id,
                        team_request_association.c.team_id,
                        team_request_association.c.sender_user_id,
                        team_request_association.c.receiver_user_id,
                        team_request_association.c.status,
                    )
                ).first()
                if row is None:
                    raise RecordNotFoundException("TEAM_REQUEST")
                rows.append(row)

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return [
            TeamRequestDTO(
                id=row.id,
                team_id=row.team_id,
                sender_user_id=row.sender_user_id,
                receiver_user_id=row.receiver_user_id,
                status=row.status,
            )
            for row in rows
        ]

    def get_team_request_by_id(self, team_request_id: int) -> TeamRequestDTO | None:
        row = self.db.execute(
            select(
                team_request_association.c.id,
                team_request_association.c.team_id,
                team_request_association.c.sender_user_id,
                team_request_association.c.receiver_user_id,
                team_request_association.c.status,
            ).where(team_request_association.c.id == team_request_id)
        ).first()

        if row is None:
            return None

        return TeamRequestDTO(
            id=row.id,
            team_id=row.team_id,
            sender_user_id=row.sender_user_id,
            receiver_user_id=row.receiver_user_id,
            status=row.status,
        )

    def update_team_request_status(
        self,
        team_request_id: int,
        status: TeamRequestStatus,
    ) -> TeamRequestDTO:
        try:
            row = self.db.execute(
                update(team_request_association)
                .where(team_request_association.c.id == team_request_id)
                .values(status=status)
                .returning(
                    team_request_association.c.id,
                    team_request_association.c.team_id,
                    team_request_association.c.sender_user_id,
                    team_request_association.c.receiver_user_id,
                    team_request_association.c.status,
                )
            ).first()
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        if row is None:
            raise RecordNotFoundException("TEAM_REQUEST")

        return TeamRequestDTO(
            id=row.id,
            team_id=row.team_id,
            sender_user_id=row.sender_user_id,
            receiver_user_id=row.receiver_user_id,
            status=row.status,
        )

    def delete_team_with_associations(self, team_id: int) -> tuple[int, int]:
        try:
            deleted_team_requests = (
                self.db.execute(
                    delete(team_request_association).where(
                        team_request_association.c.team_id == team_id
                    )
                ).rowcount
                or 0
            )

            deleted_user_team_associations = (
                self.db.execute(
                    delete(user_team_association).where(
                        user_team_association.c.team_id == team_id
                    )
                ).rowcount
                or 0
            )

            self.db.execute(delete(Team).where(Team.id == team_id))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return deleted_team_requests, deleted_user_team_associations

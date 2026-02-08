from typing import Callable
from sqlalchemy.orm import Session
from fastapi import Depends # type: ignore

from app.adapters.database.postgres.repositories.test_repository import TestRepository
from app.adapters.database.postgres.connection import get_db

def get_test_repository_read(db: Session = Depends(get_db)) -> Callable:
    return TestRepository(db).read

def get_test_repository_delete(db: Session = Depends(get_db)) -> Callable:
    return TestRepository(db).delete

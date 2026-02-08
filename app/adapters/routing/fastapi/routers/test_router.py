from typing import Callable
from fastapi import APIRouter, Depends  # type: ignore

from app.adapters.database.dependencies import (
    get_test_repository_read,
    get_test_repository_delete,
)
from app.adapters.routing.utils.decorators import format_response
from app.adapters.routing.utils.response import ResultSchema
from app.domain.dtos.test_dto import TestDTO

test_router = APIRouter(tags=["test"])

@test_router.get("/test")
@format_response
def read_test(
    id: int, use_case: Callable = Depends(get_test_repository_read)
) -> ResultSchema[TestDTO]:
    return use_case(id)

@test_router.post("/delete-test")
@format_response
def delete_test(
    id: int, use_case: Callable = Depends(get_test_repository_delete)
) -> ResultSchema[None]:
    return use_case(id)
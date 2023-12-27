from typing import Generic, TypeVar

from pydantic import BaseModel

ResultType = TypeVar("ResultType")


class APISuccess(BaseModel, Generic[ResultType]):
    ok: bool = True
    result: ResultType


class APIError(BaseModel):
    ok: bool = False
    error_code: int
    error_description: str


def create_response(result: ResultType):
    return APISuccess(result=result)

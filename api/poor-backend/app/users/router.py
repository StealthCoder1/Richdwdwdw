from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.jwt import parse_jwt_user_data
from app.users import service
from app.users.dependencies import valid_user_id
from app.users.models import User
from app.users.schemas import UsersGetResponse
from app.utils.schemas import APISuccess, create_response

router = APIRouter(tags=["Users"], dependencies=[Depends(parse_jwt_user_data)])


@router.post("/users.get", response_model=APISuccess[list[UsersGetResponse]])
async def licenses_get():
    return create_response(await service.get_users())


@router.post("/users.getById", response_model=APISuccess[UsersGetResponse])
async def licenses_get_by_id(user: Annotated[User, Depends(valid_user_id)]):
    return create_response(user)

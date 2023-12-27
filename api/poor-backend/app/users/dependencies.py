from app.users import service
from app.users.exceptions import UserNotFound
from app.users.schemas import UsersGetByIdRequest


async def valid_user_id(data: UsersGetByIdRequest):
    user = await service.get_user_by_id(data.user_id)

    if not user:
        raise UserNotFound()

    return user

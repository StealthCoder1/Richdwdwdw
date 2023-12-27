from pydantic import BaseModel


class UsersGetResponse(BaseModel):
    id: int
    username: str | None


class UserSchema(UsersGetResponse):
    email: str | None
    balance: int
    is_email_confirmed: bool


class UsersGetByIdRequest(BaseModel):
    user_id: int

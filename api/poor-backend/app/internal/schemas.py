from pydantic import BaseModel


class GetUserAccessTokenRequest(BaseModel):
    user_id: int


class UserAccessToken(BaseModel):
    access_token: str


class CreateUserByTelegramRequest(BaseModel):
    telegram_id: int
    username: str | None


class GetUserByTelegramIdRequest(BaseModel):
    telegram_id: int


class LinkTelegramUserRequest(BaseModel):
    user_id: int
    telegram_id: int
    username: str | None


class GiveUserBalanceRequest(BaseModel):
    user_id: int
    amount: int


class GetUsersCountResponse(BaseModel):
    users_count: int
    users_telegram_count: int


class GetUserRequest(BaseModel):
    username: str | None
    email: str | None


class GiveLicenseRequest(BaseModel):
    user_id: int
    license_id: str
    license_duration: int

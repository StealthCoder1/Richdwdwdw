from pydantic import BaseModel, EmailStr, Field


class SignInRequest(BaseModel):
    username: str
    password: str


class SignUpRequest(SignInRequest):
    email: EmailStr


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class JWTUserData(BaseModel):
    user_id: int = Field(alias="sub")

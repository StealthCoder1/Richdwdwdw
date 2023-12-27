from enum import StrEnum, auto

from pydantic import BaseModel


class CodePurpose(StrEnum):
    REGISTRATION = auto()


class SendConfirmEmailCodeRequest(BaseModel):
    purpose: CodePurpose


class ConfirmEmailRequest(BaseModel):
    code: str


class SendConfirmEmailCodeResponse(BaseModel):
    ttl: int
    sent: bool

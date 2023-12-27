from enum import StrEnum, auto
from typing import Literal

from pydantic import BaseModel, Field

# request


class TaskType(StrEnum):
    INVITER = auto()
    FIRST_MESSAGER = auto()
    MAILER = auto()
    AUTHORIZATION = auto()


class GetTaskRequest(BaseModel):
    type: TaskType


class StopTaskRequest(BaseModel):
    type: TaskType


# response


class MediaType(StrEnum):
    PHOTO = auto()
    VIDEO = auto()
    VIDEO_NOTE = auto()


class Media(BaseModel):
    type: MediaType
    filename: str


class Message(BaseModel):
    text: str = ""
    media: Media | None = None


class MessagesBlock(BaseModel):
    messages: list[Message]


class CooldownBlock(BaseModel):
    cooldown: int


class MailingConfig(BaseModel):
    add_to_contacts: bool | None = None
    edit_message: bool
    items: list[MessagesBlock | CooldownBlock]
    delay: float = Field(alias='messages_delay')
    auto_delete: int = Field(alias='auto_delete_messages')
    limit: int = Field(alias='messages_limit')
    forward: bool | None = Field(alias='transfer', default=None)


class InviterData(BaseModel):
    chat_id: str
    user_ids: list[str]


class MailerData(BaseModel):
    chat_ids: list[str]
    config: MailingConfig


class FirstMessagerData(BaseModel):
    chat_ids: list[str]
    config: MailingConfig


class AuthorizationData(BaseModel):
    proxies: list[str]
    sessions: list[str]


class CreateInviterTask(BaseModel):
    type: Literal[TaskType.INVITER]
    data: InviterData


class CreateMailerTask(BaseModel):
    type: Literal[TaskType.MAILER]
    data: MailerData


class CreateFirstMessagerTask(BaseModel):
    type: Literal[TaskType.FIRST_MESSAGER]
    data: FirstMessagerData


class CreateAuthorizationTask(BaseModel):
    type: Literal[TaskType.AUTHORIZATION]
    data: AuthorizationData

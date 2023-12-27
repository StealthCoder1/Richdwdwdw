from enum import StrEnum, auto

from pydantic import BaseModel


class MediaType(StrEnum):
    PHOTO = auto()
    VIDEO = auto()
    VIDEO_NOTE = auto()


class MailerTaskData(BaseModel):
    chat_ids: list[str]
    config: "MailingConfig"


class InviterTaskData(BaseModel):
    chat_id: str
    user_ids: list[str]


class FirstMessagerTaskData(BaseModel):
    chat_ids: list[str]
    config: "MailingConfig"


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

    forward: bool | None = False
    delay: float = 0
    limit: int | None = None
    delete_messages: bool = True

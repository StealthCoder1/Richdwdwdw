from typing import Any

from pydantic import BaseModel


class Message(BaseModel):
    event: str
    data: Any

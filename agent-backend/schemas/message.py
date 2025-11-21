from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MessageBase(BaseModel):
    conversation_id: int
    author: Literal["admin", "agent"]
    text: str


class MessageRead(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



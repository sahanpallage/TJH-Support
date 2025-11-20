# backend/schemas/conversation.py
from pydantic import BaseModel
from datetime import datetime


class ConversationBase(BaseModel):
    customer_id: int
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    id: int
    external_thread_id: str
    created_at: datetime

    class Config:
        from_attributes = True

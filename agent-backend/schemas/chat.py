# backend/schemas/chat.py
from pydantic import BaseModel
from typing import Any, Dict


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    reply: str
    raw: Dict[str, Any] | None = None

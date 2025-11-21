# backend/schemas/chat.py
from pydantic import BaseModel
from typing import Any, Dict, List
from schemas.message import MessageRead


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    reply: str
    raw: Dict[str, Any] | None = None
    messages: List[MessageRead]  # Return both saved messages

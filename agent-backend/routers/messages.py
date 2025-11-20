from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict, cast

from db.database import get_db
from models.conversation import Conversation
from services.job_apply_client import job_apply_client

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessageRequest(BaseModel):
  message: str
  # later can include metadata, locale, etc.

class ChatMessageResponse(BaseModel):
  reply: str
  raw: Dict[str, Any] | None = None

@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    conversation_id: int,
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
):
    # find conversation + external thread id
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    external_thread_id = cast(str, conv.external_thread_id)
    if not external_thread_id:
        raise HTTPException(status_code=500, detail="Conversation missing external thread ID")

    try:
        external_resp = await job_apply_client.send_message(
            external_thread_id=external_thread_id,
            message=payload.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send message to external agent: {e}",
        )

    # Adjust this based on actual external response shape:
    reply_text = external_resp.get("reply") or external_resp.get("message") or ""

    return ChatMessageResponse(
        reply=reply_text,
        raw=external_resp,
    )

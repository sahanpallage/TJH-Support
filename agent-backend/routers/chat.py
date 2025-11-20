# backend/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import cast

from config import settings
from db.database import get_db
from models.conversation import Conversation
from schemas.chat import ChatMessageRequest, ChatMessageResponse
from services.job_apply_client import job_apply_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    conversation_id: int,
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    external_thread_id = cast(str, conv.external_thread_id)
    
    # Try to send message to external API, with fallback in development
    external_resp = None
    if settings.environment == "development" and not settings.JOB_APPLY_API_KEY:
        # In development without API key, return a mock response
        external_resp = {
            "reply": f"Mock response: I received your message '{payload.message}'. This is a development mode response.",
            "message": payload.message,
        }
        print(f"Development mode: Returning mock response for message")
    else:
        # Try to call external API
        try:
            external_resp = await job_apply_client.send_message(
                external_thread_id=external_thread_id,
                message=payload.message,
            )
        except Exception as e:
            # In development, return mock response; in production, raise error
            if settings.environment == "development":
                external_resp = {
                    "reply": f"Mock response: I received your message '{payload.message}'. External API unavailable ({str(e)[:50]}...).",
                    "message": payload.message,
                }
                print(f"Warning: External API failed ({e}), returning mock response")
            else:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to send message to external agent: {e}",
                )

    # TODO: adjust field name based on actual response
    reply_text = (
        external_resp.get("reply")
        or external_resp.get("message")
        or external_resp.get("content")
        or ""
    )

    return ChatMessageResponse(reply=reply_text, raw=external_resp)

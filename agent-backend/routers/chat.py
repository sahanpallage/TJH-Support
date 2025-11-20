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
    
    # Send message to the live Donely agent
    try:
        external_resp = await job_apply_client.send_message(
            thread_id=external_thread_id,
            message=payload.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send message to agent: {str(e)}",
        )

    # Parse the response from LangGraph API
    # The response typically contains a state with messages
    reply_text = _extract_reply_from_response(external_resp)

    return ChatMessageResponse(reply=reply_text, raw=external_resp)


def _extract_reply_from_response(resp: dict) -> str:
    """
    Extract the assistant's reply from the LangGraph response.
    The response structure from Donely includes:
    - messages: array of message objects
    - Each message has 'type' (human/ai) and 'content'
    - We want the last 'ai' type message's content
    """
    try:
        # Check if response has 'messages' array (LangGraph format)
        messages = resp.get("messages", [])
        if messages:
            # Get the last message from the assistant (type='ai')
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("type") == "ai":
                    content = msg.get("content", "")
                    if content:
                        return content
            
            # Fallback: just return the last message's content
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                return last_msg.get("content", "")
        
        # Fallback: check for direct message/reply fields
        if "reply" in resp:
            return resp.get("reply", "")
        if "message" in resp:
            return resp.get("message", "")
        if "content" in resp:
            return resp.get("content", "")
        
        # If we can't parse, return the whole response as string
        return str(resp)
    except Exception as e:
        print(f"Error parsing response: {e}")
        return f"Agent response received but parsing failed: {str(e)}"


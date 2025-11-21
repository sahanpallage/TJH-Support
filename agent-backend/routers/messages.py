from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.conversation import Conversation
from models.message import Message
from schemas.message import MessageRead

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/conversation/{conversation_id}", response_model=List[MessageRead])
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """Get all messages for a conversation."""
    # Verify conversation exists
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found"
        )

    # Get all messages for this conversation
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages

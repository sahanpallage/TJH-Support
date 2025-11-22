# backend/routers/conversations.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config import settings
from db.database import get_db
from models.conversation import Conversation
from schemas.conversation import ConversationCreate, ConversationRead
from services.openai_client import get_openai_client

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
):
    # Create a new thread on the OpenAI assistant
    try:
        client = get_openai_client()
        print(f"[Conversations] Using OpenAI Assistant API")
        
        external_resp = await client.create_thread()
        external_thread_id = external_resp.get("thread_id") or external_resp.get("id")
        
        if not external_thread_id:
            raise ValueError(f"OpenAI did not return a thread ID. Response: {external_resp}")
        
        print(f"[Conversations] Created OpenAI thread with ID: {external_thread_id}")
    except Exception as e:
        print(f"[Conversations] Error creating OpenAI thread: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Failed to create conversation thread: {str(e)}",
        )

    # Store in local database
    conv = Conversation(
        customer_id=payload.customer_id,
        title=payload.title,
        external_thread_id=external_thread_id,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/customer/{customer_id}", response_model=List[ConversationRead])
def list_customer_conversations(customer_id: int, db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.customer_id == customer_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return conversations


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conv)
    db.commit()
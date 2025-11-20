# backend/routers/conversations.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config import settings
from db.database import get_db
from models.conversation import Conversation
from schemas.conversation import ConversationCreate, ConversationRead
from services.job_apply_client import job_apply_client

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
):
    # 1) Try to create external session, fallback to mock ID in development
    external_thread_id = None
    
    if settings.environment == "development" and not settings.JOB_APPLY_API_KEY:
        # In development without API key, use a mock thread ID
        external_thread_id = f"mock-{uuid.uuid4().hex[:16]}"
        print(f"Development mode: Using mock external_thread_id: {external_thread_id}")
    else:
        # Try to call external API
        try:
            external_resp = await job_apply_client.create_conversation(
                customer_id=payload.customer_id,
                title=payload.title,
            )
            # TODO adjust key according to swagger response
            external_thread_id = (
                external_resp.get("thread_id")
                or external_resp.get("id")
                or external_resp.get("session_id")
            )
            if not external_thread_id:
                raise ValueError("External API did not return a thread ID")
        except Exception as e:
            # In development, fallback to mock ID; in production, raise error
            if settings.environment == "development":
                external_thread_id = f"mock-{uuid.uuid4().hex[:16]}"
                print(f"Warning: External API failed ({e}), using mock ID: {external_thread_id}")
            else:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to create external conversation: {e}",
                )

    # 2) store in local DB
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
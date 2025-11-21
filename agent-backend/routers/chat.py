# backend/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import cast, List, Optional

from config import settings
from db.database import get_db
from models.conversation import Conversation
from models.message import Message
from schemas.chat import ChatMessageRequest, ChatMessageResponse
from schemas.message import MessageRead
from services.job_apply_client import job_apply_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Send a chat message with optional file attachments.
    Supports both:
    - JSON: {"message": "text"} (backward compatible)
    - FormData: message=text&files=file1&files=file2 (for file uploads)
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    external_thread_id = cast(str, conv.external_thread_id)
    customer_id = cast(int, conv.customer_id)  # Cast to int for type safety
    
    # Check content type to determine if it's FormData or JSON
    content_type = request.headers.get("content-type", "")
    message_text = ""
    files: List[UploadFile] = []
    
    if "multipart/form-data" in content_type:
        # FormData request - parse form data
        form = await request.form()
        message_field = form.get("message")
        if message_field:
            message_text = str(message_field) if isinstance(message_field, str) else ""
        file_list = form.getlist("files")
        files = [f for f in file_list if isinstance(f, UploadFile)]
    else:
        # JSON request - parse JSON body
        try:
            body = await request.json()
            payload = ChatMessageRequest(**body)
            message_text = payload.message
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request format: {str(e)}",
            )
    
    uploaded_file_info = []
    
    # Upload files to the agent if provided
    if files:
        for file in files:
            try:
                file_contents = await file.read()
                # Upload file to the agent
                await job_apply_client.upload_document(
                    customer_id=customer_id,
                    file_bytes=file_contents,
                    filename=file.filename or "uploaded_file",
                    content_type=file.content_type or "application/octet-stream",
                )
                uploaded_file_info.append(f"{file.filename} ({len(file_contents)} bytes)")
            except Exception as e:
                # Log error but continue - don't fail the whole message
                print(f"Warning: Failed to upload file {file.filename}: {e}")
    
    # Append file information to message
    if uploaded_file_info:
        file_list = ", ".join(uploaded_file_info)
        if message_text:
            message_text = f"{message_text}\n\n[Uploaded files: {file_list}]"
        else:
            message_text = f"[Uploaded files: {file_list}]"
    
    # Ensure message_text is a string
    message_text = str(message_text) if message_text else ""
    
    # Save admin message to database
    admin_message = Message(
        conversation_id=conversation_id,
        author="admin",
        text=message_text,
    )
    db.add(admin_message)
    db.flush()  # Flush to get the ID, but don't commit yet
    
    # Send message to the live Donely agent
    try:
        external_resp = await job_apply_client.send_message(
            thread_id=external_thread_id,
            message=message_text,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send message to agent: {str(e)}",
        )

    # Parse the response from LangGraph API
    # The response typically contains a state with messages
    reply_text = _extract_reply_from_response(external_resp)

    # Save agent response to database
    agent_message = Message(
        conversation_id=conversation_id,
        author="agent",
        text=reply_text,
    )
    db.add(agent_message)
    db.commit()  # Commit both messages together
    db.refresh(admin_message)
    db.refresh(agent_message)

    # Return both saved messages along with the response
    return ChatMessageResponse(
        reply=reply_text,
        raw=external_resp,
        messages=[
            MessageRead.model_validate(admin_message),
            MessageRead.model_validate(agent_message),
        ],
    )


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


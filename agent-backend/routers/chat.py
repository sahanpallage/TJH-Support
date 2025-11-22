# backend/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import cast, List, Optional, Dict, Any

from config import settings
from db.database import get_db
from models.conversation import Conversation
from models.message import Message
from schemas.chat import ChatMessageRequest, ChatMessageResponse
from schemas.message import MessageRead
from services.openai_client import get_openai_client

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
    content_type = request.headers.get("content-type", "").lower()
    message_text = ""
    files: List[UploadFile] = []
    
    print(f"[Chat] Request content-type: {content_type}")
    
    if "multipart/form-data" in content_type:
        # FormData request - parse form data using FastAPI's form parser
        try:
            form = await request.form()
            print(f"[Chat] Form keys: {list(form.keys())}")
            
            # Get message field
            message_field = form.get("message")
            if message_field:
                message_text = str(message_field) if isinstance(message_field, str) else ""
            
            # Get all files - FastAPI's form.getlist returns a list
            file_list = form.getlist("files")
            print(f"[Chat] Raw file_list: type={type(file_list)}, length={len(file_list)}")
            
            # Check each item in the list
            # Note: FastAPI's UploadFile is actually starlette.datastructures.UploadFile
            # We check for the attributes instead of using isinstance
            for idx, item in enumerate(file_list):
                print(f"[Chat] File item[{idx}]: type={type(item)}, has filename={hasattr(item, 'filename')}, has read={hasattr(item, 'read')}")
                
                # Check if it's an UploadFile-like object (has filename and read method)
                if hasattr(item, 'filename') and hasattr(item, 'read') and hasattr(item, 'content_type'):
                    # Cast to UploadFile for type safety (form.getlist can return str or UploadFile)
                    upload_file = cast(UploadFile, item)
                    files.append(upload_file)
                    print(f"[Chat] Added file[{idx}]: {upload_file.filename}")
                else:
                    print(f"[Chat] WARNING: Item {idx} is not a valid UploadFile: {item}")
            
            print(f"[Chat] Received FormData: message='{message_text}', files={len(files)}")
            for idx, f in enumerate(files):
                print(f"[Chat] File[{idx}]: {f.filename}, type: {f.content_type}")
        except Exception as e:
            print(f"[Chat] ERROR parsing FormData: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Failed to parse FormData: {str(e)}")
    else:
        # JSON request - parse JSON body
        try:
            body = await request.json()
            payload = ChatMessageRequest(**body)
            message_text = payload.message
            print(f"[Chat] Received JSON: message='{message_text}'")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request format: {str(e)}",
            )
    
    # Prepare files - try uploading to thread first, then reference in message
    file_attachments: List[Dict[str, Any]] = []
    file_names_list = []
    uploaded_file_ids = []
    
    # Get OpenAI client
    client = get_openai_client()
    print(f"[Chat] Using OpenAI Assistant API")
    
    # Process files - try to upload them to the thread first
    if files:
        print(f"[Chat] Processing {len(files)} file(s) - attempting to upload to thread first...")
        for file in files:
            try:
                file_contents = await file.read()
                file_size = len(file_contents)
                file_name = file.filename or "uploaded_file"
                file_type = file.content_type or "application/pdf"
                
                print(f"[Chat] Attempting to upload file: {file_name} ({file_size} bytes) to thread {external_thread_id}...")
                
                # Try to upload file to the thread first
                file_id = await client.upload_document(
                    customer_id=customer_id,
                    file_bytes=file_contents,
                    filename=file_name,
                    content_type=file_type,
                    thread_id=external_thread_id,
                )
                
                if file_id:
                    uploaded_file_ids.append(file_id)
                    print(f"[Chat] File uploaded successfully, file_id: {file_id}")
                else:
                    # Upload failed or didn't return file_id - fall back to including in message
                    print(f"[Chat] File upload did not return file_id, will include in message payload")
                    file_attachments.append({
                        "name": file_name,
                        "content": file_contents,
                        "type": file_type,
                    })
                
                file_names_list.append(file_name)
                print(f"[Chat] Successfully prepared file: {file_name}")
            except Exception as e:
                # Log error but continue - don't fail the whole message
                print(f"[Chat] ERROR: Failed to process file {file.filename}: {e}")
                import traceback
                traceback.print_exc()
    
    # Build message text with file information
    if file_names_list:
        file_names = ", ".join(file_names_list)
        file_instruction = f"\n\nI have attached {len(file_names_list)} file(s) with this message: {file_names}. Please read and analyze the content of these files."
        
        if message_text:
            message_text = f"{message_text}{file_instruction}"
        else:
            message_text = f"Please process the following attached files: {file_names}.{file_instruction}"
    
    # Ensure message_text is a string
    message_text = str(message_text) if message_text else ""
    
    print(f"[Chat] Sending message to agent: '{message_text[:100]}...' (length: {len(message_text)})")
    print(f"[Chat] Including {len(file_attachments)} file(s) in message payload")
    
    # Save admin message to database
    admin_message = Message(
        conversation_id=conversation_id,
        author="admin",
        text=message_text,
    )
    db.add(admin_message)
    db.flush()  # Flush to get the ID, but don't commit yet
    
    # Send message to the agent with file attachments
    try:
        print(f"[Chat] Sending message to agent thread: {external_thread_id}")
        print(f"[Chat] Using {len(uploaded_file_ids)} file_id(s) and {len(file_attachments)} file(s) in payload")
        external_resp = await client.send_message(
            thread_id=external_thread_id,
            message=message_text,
            file_ids=uploaded_file_ids if uploaded_file_ids else None,
            files=file_attachments if file_attachments else None,
        )
        print(f"[Chat] Agent response received: {type(external_resp)}")
    except Exception as e:
        db.rollback()
        error_detail = str(e)
        error_type = type(e).__name__
        print(f"[Chat] ERROR sending to agent ({error_type}): {error_detail}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send message to agent: {error_detail}",
        )

    # Parse the response from LangGraph API
    # Check for errors first
    print(f"[Chat] Full agent response: {external_resp}")
    if "error" in external_resp:
        error_info = external_resp.get("error", {})
        error_msg = error_info.get("message", "Unknown error")
        print(f"[Chat] Agent returned error: {error_info}")
        # Try to extract more details
        if isinstance(error_msg, dict):
            nested_error = error_msg.get("error", {}).get("message", str(error_msg))
            reply_text = f"Error from agent: {nested_error}"
        else:
            reply_text = f"Error from agent: {error_msg}"
    else:
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
    Extract the assistant's reply from the OpenAI response.
    The response structure includes:
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


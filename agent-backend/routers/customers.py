# backend/routers/customers.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from db.database import get_db
from models.customer import Customer
from models.document import Document
from models.conversation import Conversation
from schemas.customer import CustomerCreate, CustomerRead
from schemas.document import DocumentRead
from services.openai_client import get_openai_client

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerRead)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/", response_model=List[CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


class ChatRequest(BaseModel):
    message: str


class AnalyzeRequest(BaseModel):
    document_ids: Optional[List[int]] = None


class JobSearchRequest(BaseModel):
    preferences: Optional[str] = None


@router.post("/{customer_id}/documents", response_model=DocumentRead)
async def upload_customer_document(
    customer_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Upload a document for a customer.
    - Receives PDF from frontend
    - Saves it to database (Supabase/Postgres)
    - Uploads to OpenAI Files API
    - Returns document record with OpenAI file_id
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    contents = await file.read()
    filename = file.filename or "uploaded_file"
    content_type = file.content_type or "application/pdf"
    
    # Upload to OpenAI
    openai_file_id = None
    try:
        client = get_openai_client()
        openai_file_id = await client.upload_document(
            customer_id=customer_id,
            file_bytes=contents,
            filename=filename,
            content_type=content_type,
        )
        print(f"[Customers] Uploaded document to OpenAI, file_id: {openai_file_id}")
    except Exception as e:
        print(f"[Customers] Warning: Failed to upload document to OpenAI: {e}")
        # Continue - we'll still save the document record
    
    # Save document record to database
    doc = Document(
        customer_id=customer_id,
        title=title or filename,
        url=f"openai://files/{openai_file_id}" if openai_file_id else f"/files/{filename}",
        type="resume",  # Default type, can be made configurable
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return doc


@router.post("/{customer_id}/chat")
async def customer_chat(
    customer_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Chat with the assistant for a specific customer.
    Creates or uses existing conversation thread.
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get or create conversation for this customer
    conv = db.query(Conversation).filter(
        Conversation.customer_id == customer_id
    ).order_by(Conversation.created_at.desc()).first()
    
    if not conv:
        # Create new conversation
        client = get_openai_client()
        thread_resp = await client.create_thread()
        thread_id = thread_resp.get("thread_id") or thread_resp.get("id")
        
        conv = Conversation(
            customer_id=customer_id,
            title="Customer Chat",
            external_thread_id=thread_id,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    # Send message
    client = get_openai_client()
    thread_id = str(conv.external_thread_id)  # Cast to str for type safety
    response = await client.send_message(
        thread_id=thread_id,
        message=request.message,
    )
    
    return response


@router.post("/{customer_id}/analyze")
async def analyze_customer_documents(
    customer_id: int,
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
):
    """
    Analyze customer documents using the assistant.
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get documents to analyze
    if request.document_ids:
        documents = db.query(Document).filter(
            Document.customer_id == customer_id,
            Document.id.in_(request.document_ids)
        ).all()
    else:
        # Analyze all documents for this customer
        documents = db.query(Document).filter(
            Document.customer_id == customer_id
        ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for analysis")
    
    # Get or create conversation thread
    conv = db.query(Conversation).filter(
        Conversation.customer_id == customer_id
    ).order_by(Conversation.created_at.desc()).first()
    
    if not conv:
        client = get_openai_client()
        thread_resp = await client.create_thread()
        thread_id = thread_resp.get("thread_id") or thread_resp.get("id")
        
        conv = Conversation(
            customer_id=customer_id,
            title="Document Analysis",
            external_thread_id=thread_id,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    # Extract OpenAI file IDs from documents
    file_ids = []
    for doc in documents:
        # Extract file_id from URL if it's an OpenAI file URL
        doc_url = str(doc.url)  # Cast to str for type safety
        if doc_url.startswith("openai://files/"):
            file_id = doc_url.replace("openai://files/", "")
            file_ids.append(file_id)
    
    # Create analysis message
    analysis_prompt = f"Please analyze the following {len(documents)} document(s) for customer {customer_id}."
    
    # Send message with file attachments
    client = get_openai_client()
    thread_id = str(conv.external_thread_id)  # Cast to str for type safety
    response = await client.send_message(
        thread_id=thread_id,
        message=analysis_prompt,
        file_ids=file_ids if file_ids else None,
    )
    
    return response


@router.post("/{customer_id}/job-search")
async def search_jobs_for_customer(
    customer_id: int,
    request: JobSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Search for jobs based on customer's resume and preferences.
    Returns jobs in CSV format.
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get customer's documents (resume, preferences)
    documents = db.query(Document).filter(
        Document.customer_id == customer_id
    ).all()
    
    # Extract OpenAI file IDs
    file_ids = []
    for doc in documents:
        doc_url = str(doc.url)  # Cast to str for type safety
        if doc_url.startswith("openai://files/"):
            file_id = doc_url.replace("openai://files/", "")
            file_ids.append(file_id)
    
    # Get or create conversation thread
    conv = db.query(Conversation).filter(
        Conversation.customer_id == customer_id
    ).order_by(Conversation.created_at.desc()).first()
    
    if not conv:
        client = get_openai_client()
        thread_resp = await client.create_thread()
        thread_id = thread_resp.get("thread_id") or thread_resp.get("id")
        
        conv = Conversation(
            customer_id=customer_id,
            title="Job Search",
            external_thread_id=thread_id,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    # Create job search prompt
    job_search_prompt = """
Analyze the uploaded resume and job preference file.

Give me 10 jobs posted within the last 5 days.

Return in CSV format with columns:
Job_Title, Company, Location, Salary_Range, Work_Type, Job_URL, Description_Summary, Match_Score, Priority, Percentage
"""
    
    if request.preferences:
        job_search_prompt += f"\n\nAdditional preferences: {request.preferences}"
    
    # Send message with file attachments
    client = get_openai_client()
    thread_id = str(conv.external_thread_id)  # Cast to str for type safety
    response = await client.send_message(
        thread_id=thread_id,
        message=job_search_prompt,
        file_ids=file_ids if file_ids else None,
    )
    
    return response

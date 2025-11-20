# backend/routers/documents.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.document import Document
from schemas.document import DocumentCreate, DocumentRead
from services.job_apply_client import job_apply_client

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    customer_id: int,
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()

    # optionally send to external job-apply agent
    try:
        _ = await job_apply_client.upload_document(
            customer_id=customer_id,
            file_bytes=contents,
            filename=file.filename or "uploaded_file",
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to upload document to external agent: {e}",
        )

    # store document record (here we assume URL is a GDrive link passed as title for now)
    doc = Document(
        customer_id=customer_id,
        title=title,
        url=f"/files/{file.filename or 'uploaded_file'}",  # TODO: replace with real storage URL
        type="resume",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

# backend/schemas/document.py
from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
    customer_id: int
    title: str
    url: str
    type: str | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

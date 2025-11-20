# backend/models/document.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)  # link to Google Drive or storage
    type = Column(String, nullable=True)  # "resume", "360", etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="documents")

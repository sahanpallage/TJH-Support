from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    author = Column(
        Enum("admin", "agent", name="message_author"),
        nullable=False,
    )
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")



# backend/models/__init__.py

# This file allows easier imports:
from .customer import Customer
from .conversation import Conversation
from .document import Document

__all__ = ["Customer", "Conversation", "Document"]

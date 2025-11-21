from db.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
# Import model classes explicitly so SQLAlchemy registers them with Base
from models.customer import Customer  # noqa: F401
from models.conversation import Conversation  # noqa: F401
from models.document import Document  # noqa: F401
from models.message import Message  # noqa: F401
from routers import customers, conversations, chat, documents, messages

# Create tables only in development mode
# Note: create_all() is idempotent - it only creates tables that don't exist
# For production, use Alembic migrations instead
if settings.environment == "development":
    try:
        print("Creating database tables (development mode)...")
        Base.metadata.create_all(bind=engine)
        print(f"Tables ready. Available tables: {list(Base.metadata.tables.keys())}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
else:
    print("Skipping table creation (production mode - use migrations)")

app = FastAPI(title="JobProMax Internal API", version="0.1.0")

origins = settings.allowed_origins or [settings.frontend_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(messages.router)

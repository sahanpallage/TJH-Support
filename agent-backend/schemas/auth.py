# backend/schemas/auth.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, e.g., 'bearer")

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

class UserInDB(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] 
    hashed_password: str
    is_active: bool
    is_employer: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
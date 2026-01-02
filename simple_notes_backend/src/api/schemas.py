from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class HealthResponse(BaseModel):
    message: str = Field(..., description="Health status message")


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address (unique).")
    password: str = Field(..., min_length=6, description="User password (min 6 chars).")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., description="User password.")


class UserOut(BaseModel):
    id: UUID = Field(..., description="User ID.")
    email: EmailStr = Field(..., description="User email.")
    created_at: datetime = Field(..., description="Creation timestamp.")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field("bearer", description="Token type.")


class NoteCreate(BaseModel):
    title: str = Field("", description="Note title.")
    content: str = Field("", description="Note content.")


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated note title.")
    content: Optional[str] = Field(None, description="Updated note content.")


class NoteOut(BaseModel):
    id: UUID = Field(..., description="Note ID.")
    user_id: UUID = Field(..., description="Owner user ID.")
    title: str = Field(..., description="Note title.")
    content: str = Field(..., description="Note content.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")

    model_config = {"from_attributes": True}

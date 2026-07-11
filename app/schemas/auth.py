from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=32)


class UserResponse(UserBase):
    id: UUID
    name: Optional[str]
    created_at: datetime
    updated_at: datetime

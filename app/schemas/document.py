from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.auth import UserResponse


class DocBase(BaseModel):
    name: str


class DocPartialResponse(DocBase):
    id: UUID
    created_at: datetime
    creator: Optional[UserResponse] = None
    last_updated: datetime
    access_only_me: bool

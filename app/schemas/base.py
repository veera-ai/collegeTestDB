from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class BaseSchema(BaseModel):
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

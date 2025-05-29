from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.models.content import NewsCategory, EventStatus
from app.schemas.base import BaseSchema

class NewsBase(BaseModel):
    title: str
    content: str
    category: NewsCategory
    published_at: datetime

class NewsCreate(NewsBase):
    author_id: UUID

class NewsUpdate(NewsBase):
    pass

class News(NewsBase, BaseSchema):
    id: UUID
    author_id: UUID

class EventBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    status: EventStatus = EventStatus.SCHEDULED

class EventCreate(EventBase):
    organizer_id: UUID

class EventUpdate(EventBase):
    pass

class Event(EventBase, BaseSchema):
    id: UUID
    organizer_id: UUID

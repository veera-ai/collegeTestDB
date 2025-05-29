from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models.base import Base

class NewsCategory(str, enum.Enum):
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    EVENTS = "events"
    GENERAL = "general"

class News(Base):
    """News model for college announcements and updates."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(SQLEnum(NewsCategory), nullable=False)
    published_at = Column(DateTime, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

class EventStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Event(Base):
    """Event model for college events and activities."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.SCHEDULED)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    # Relationships
    registrations = relationship("Registration", back_populates="event")

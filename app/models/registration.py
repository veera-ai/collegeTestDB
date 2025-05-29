from sqlalchemy import Column, ForeignKey, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

class Registration(Base):
    """Registration model for event participation."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("event.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    attended = Column(Boolean, default=False)
    feedback = Column(String)

    # Relationships
    event = relationship("Event", back_populates="registrations")

class Report(Base):
    """Report model for generating and storing reports."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    report_type = Column(String, nullable=False)
    parameters = Column(JSON)
    result_data = Column(JSON)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

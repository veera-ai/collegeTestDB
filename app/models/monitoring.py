from sqlalchemy import Column, String, JSON, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

class Dashboard(Base):
    """Dashboard model for user-specific dashboard configurations."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False)
    layout = Column(JSON)
    widgets = Column(JSON)
    is_default = Column(Boolean, default=False)

class AuditLog(Base):
    """Audit log model for tracking system activities."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    changes = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    details = Column(Text)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

from typing import Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID
from app.schemas.base import BaseSchema

class DashboardBase(BaseModel):
    title: str
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[Dict[str, Any]] = None
    is_default: bool = False

class DashboardCreate(DashboardBase):
    user_id: UUID

class DashboardUpdate(DashboardBase):
    pass

class Dashboard(DashboardBase, BaseSchema):
    id: UUID
    user_id: UUID

class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: str
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    user_id: UUID

class AuditLogUpdate(AuditLogBase):
    pass

class AuditLog(AuditLogBase, BaseSchema):
    id: UUID
    user_id: UUID

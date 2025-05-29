from typing import Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID
from app.schemas.base import BaseSchema

class RegistrationBase(BaseModel):
    attended: bool = False
    feedback: Optional[str] = None

class RegistrationCreate(RegistrationBase):
    event_id: UUID
    user_id: UUID

class RegistrationUpdate(RegistrationBase):
    pass

class Registration(RegistrationBase, BaseSchema):
    id: UUID
    event_id: UUID
    user_id: UUID

class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: str
    parameters: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    generated_by: UUID

class ReportUpdate(ReportBase):
    pass

class Report(ReportBase, BaseSchema):
    id: UUID
    generated_by: UUID

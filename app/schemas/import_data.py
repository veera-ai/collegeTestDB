"""Schemas for bulk data import functionality."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema
from app.models.user import UserRole
from enum import Enum

class EntityType(str, Enum):
    """Supported entity types for bulk import."""
    USER = "user"
    STUDENT = "student"
    STAFF = "staff"
    ENROLLMENT = "enrollment"
    GRADE = "grade"
    ATTENDANCE = "attendance"
    NEWS = "news"
    EVENT = "event"
    REGISTRATION = "registration"
    DASHBOARD = "dashboard"
    REPORT = "report"

class ImportRequest(BaseModel):
    """Schema for bulk import request."""
    entity: EntityType
    data: List[Dict[str, Any]] = Field(..., description="List of records to import")

class ImportValidationError(BaseModel):
    """Schema for validation errors during import."""
    index: int
    errors: Dict[str, List[str]]

class ImportResponse(BaseModel):
    """Schema for bulk import response."""
    success: bool
    message: str
    total_records: int
    processed_records: int
    failed_records: int
    validation_errors: List[ImportValidationError] = []
    inserted_ids: List[str] = []

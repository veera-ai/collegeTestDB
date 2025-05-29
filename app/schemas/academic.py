from typing import Optional, Dict, Any
from pydantic import BaseModel, constr
from datetime import date
from uuid import UUID
from app.schemas.base import BaseSchema

class StudentBase(BaseModel):
    enrollment_number: constr(min_length=5, max_length=20)
    date_of_birth: date
    address: Optional[str] = None
    personal_info: Optional[Dict[str, Any]] = None
    enrollment_year: constr(min_length=4, max_length=4)
    current_semester: Optional[constr(min_length=1, max_length=2)] = None

class StudentCreate(StudentBase):
    user_id: UUID

class StudentUpdate(StudentBase):
    pass

class Student(StudentBase, BaseSchema):
    id: UUID
    user_id: UUID

class StaffBase(BaseModel):
    employee_id: constr(min_length=5, max_length=20)
    department: str
    designation: str
    date_of_joining: date
    qualifications: Optional[Dict[str, Any]] = None

class StaffCreate(StaffBase):
    user_id: UUID

class StaffUpdate(StaffBase):
    pass

class Staff(StaffBase, BaseSchema):
    id: UUID
    user_id: UUID

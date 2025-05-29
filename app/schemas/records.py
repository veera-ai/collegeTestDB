from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from app.models.records import EnrollmentStatus
from app.schemas.base import BaseSchema

class EnrollmentBase(BaseModel):
    course_code: str
    semester: str
    academic_year: str
    status: EnrollmentStatus = EnrollmentStatus.PENDING

class EnrollmentCreate(EnrollmentBase):
    student_id: UUID

class EnrollmentUpdate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase, BaseSchema):
    id: UUID
    student_id: UUID

class GradeBase(BaseModel):
    grade_value: float = Field(..., ge=0, le=100)
    max_grade: float = Field(100.0, ge=0)
    remarks: Optional[str] = None

class GradeCreate(GradeBase):
    student_id: UUID
    staff_id: UUID
    enrollment_id: UUID

class GradeUpdate(GradeBase):
    pass

class Grade(GradeBase, BaseSchema):
    id: UUID
    student_id: UUID
    staff_id: UUID
    enrollment_id: UUID

class AttendanceBase(BaseModel):
    date: date
    is_present: bool = False
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    student_id: UUID
    enrollment_id: UUID

class AttendanceUpdate(AttendanceBase):
    pass

class Attendance(AttendanceBase, BaseSchema):
    id: UUID
    student_id: UUID
    enrollment_id: UUID

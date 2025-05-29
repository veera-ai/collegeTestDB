from sqlalchemy import Column, String, ForeignKey, Date, Integer, Float, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models.base import Base

class EnrollmentStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"

class Enrollment(Base):
    """Enrollment model for tracking student course enrollments."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    course_code = Column(String, nullable=False)
    semester = Column(String(2), nullable=False)
    academic_year = Column(String(4), nullable=False)
    status = Column(SQLEnum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.PENDING)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    grades = relationship("Grade", back_populates="enrollment")
    attendance = relationship("Attendance", back_populates="enrollment")

class Grade(Base):
    """Grade model for tracking student performance."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollment.id"), nullable=False)
    grade_value = Column(Float, nullable=False)
    max_grade = Column(Float, default=100.0)
    remarks = Column(String)

    # Relationships
    student = relationship("Student", back_populates="grades")
    staff = relationship("Staff", back_populates="grades")
    enrollment = relationship("Enrollment", back_populates="grades")

class Attendance(Base):
    """Attendance model for tracking student attendance."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollment.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_present = Column(Boolean, default=False)
    remarks = Column(String)

    # Relationships
    student = relationship("Student", back_populates="attendance")
    enrollment = relationship("Enrollment", back_populates="attendance")

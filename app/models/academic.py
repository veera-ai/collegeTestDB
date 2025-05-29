from sqlalchemy import Column, String, ForeignKey, Date, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

class Student(Base):
    """Student model with academic and personal information."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    enrollment_number = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    address = Column(Text)
    personal_info = Column(JSON)
    enrollment_year = Column(String(4), nullable=False)
    current_semester = Column(String(2))

    # Relationships
    user = relationship("User", back_populates="student")
    enrollments = relationship("Enrollment", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    attendance = relationship("Attendance", back_populates="student")

class Staff(Base):
    """Staff model for teachers and administrative staff."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    date_of_joining = Column(Date, nullable=False)
    qualifications = Column(JSON)

    # Relationships
    user = relationship("User", back_populates="staff")
    grades = relationship("Grade", back_populates="staff")

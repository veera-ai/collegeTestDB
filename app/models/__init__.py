from app.models.base import Base
from app.models.user import User, UserRole
from app.models.academic import Student, Staff
from app.models.records import Enrollment, Grade, Attendance, EnrollmentStatus
from app.models.content import News, Event, NewsCategory, EventStatus
from app.models.registration import Registration, Report
from app.models.monitoring import Dashboard, AuditLog

# For easier access to all models
__all__ = [
    "Base",
    "User",
    "UserRole",
    "Student",
    "Staff",
    "Enrollment",
    "Grade",
    "Attendance",
    "EnrollmentStatus",
    "News",
    "Event",
    "NewsCategory",
    "EventStatus",
    "Registration",
    "Report",
    "Dashboard",
    "AuditLog",
]

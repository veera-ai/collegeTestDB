from app.schemas.base import BaseSchema
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.academic import Student, StudentCreate, StudentUpdate, Staff, StaffCreate, StaffUpdate
from app.schemas.records import Enrollment, EnrollmentCreate, EnrollmentUpdate, Grade, GradeCreate, GradeUpdate, Attendance, AttendanceCreate, AttendanceUpdate
from app.schemas.content import News, NewsCreate, NewsUpdate, Event, EventCreate, EventUpdate
from app.schemas.registration import Registration, RegistrationCreate, RegistrationUpdate, Report, ReportCreate, ReportUpdate
from app.schemas.monitoring import Dashboard, DashboardCreate, DashboardUpdate, AuditLog, AuditLogCreate, AuditLogUpdate

# For easier access to all schemas
__all__ = [
    "BaseSchema",
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Student",
    "StudentCreate",
    "StudentUpdate",
    "Staff",
    "StaffCreate",
    "StaffUpdate",
    "Enrollment",
    "EnrollmentCreate",
    "EnrollmentUpdate",
    "Grade",
    "GradeCreate",
    "GradeUpdate",
    "Attendance",
    "AttendanceCreate",
    "AttendanceUpdate",
    "News",
    "NewsCreate",
    "NewsUpdate",
    "Event",
    "EventCreate",
    "EventUpdate",
    "Registration",
    "RegistrationCreate",
    "RegistrationUpdate",
    "Report",
    "ReportCreate",
    "ReportUpdate",
    "Dashboard",
    "DashboardCreate",
    "DashboardUpdate",
    "AuditLog",
    "AuditLogCreate",
    "AuditLogUpdate",
]

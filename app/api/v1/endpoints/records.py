"""Records management endpoints for enrollments, grades and attendance."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    check_user_role
)
from app.models.user import User, UserRole
from app.models.records import Enrollment, Grade, Attendance, EnrollmentStatus
from app.schemas.records import (
    Enrollment as EnrollmentSchema,
    EnrollmentCreate,
    EnrollmentUpdate,
    Grade as GradeSchema,
    GradeCreate,
    GradeUpdate,
    Attendance as AttendanceSchema,
    AttendanceCreate,
    AttendanceUpdate
)

router = APIRouter()

# Enrollment endpoints
# PUBLIC_INTERFACE
@router.get("/enrollments/", response_model=List[EnrollmentSchema])
def get_enrollments(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get list of enrollments."""
    enrollments = db.query(Enrollment).offset(skip).limit(limit).all()
    return enrollments

# PUBLIC_INTERFACE
@router.post("/enrollments/", response_model=EnrollmentSchema)
def create_enrollment(
    *,
    db: Session = Depends(get_db),
    enrollment_in: EnrollmentCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new enrollment."""
    # Check if student exists and enrollment is unique
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment_in.student_id,
        Enrollment.course_code == enrollment_in.course_code,
        Enrollment.semester == enrollment_in.semester,
        Enrollment.academic_year == enrollment_in.academic_year
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Student is already enrolled in this course for the given semester.",
        )
    
    enrollment = Enrollment(**enrollment_in.dict())
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

# PUBLIC_INTERFACE
@router.get("/enrollments/{enrollment_id}", response_model=EnrollmentSchema)
def get_enrollment(
    enrollment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get enrollment by ID."""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment

# PUBLIC_INTERFACE
@router.put("/enrollments/{enrollment_id}", response_model=EnrollmentSchema)
def update_enrollment(
    *,
    db: Session = Depends(get_db),
    enrollment_id: str,
    enrollment_in: EnrollmentUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update enrollment."""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    for field, value in enrollment_in.dict(exclude_unset=True).items():
        setattr(enrollment, field, value)
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

# PUBLIC_INTERFACE
@router.delete("/enrollments/{enrollment_id}", response_model=EnrollmentSchema)
def delete_enrollment(
    *,
    db: Session = Depends(get_db),
    enrollment_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete enrollment."""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
    return enrollment

# Grade endpoints
# PUBLIC_INTERFACE
@router.get("/grades/", response_model=List[GradeSchema])
def get_grades(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get list of grades."""
    grades = db.query(Grade).offset(skip).limit(limit).all()
    return grades

# PUBLIC_INTERFACE
@router.post("/grades/", response_model=GradeSchema)
def create_grade(
    *,
    db: Session = Depends(get_db),
    grade_in: GradeCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new grade."""
    # Verify enrollment exists and belongs to student
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == grade_in.enrollment_id,
        Enrollment.student_id == grade_in.student_id
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=400,
            detail="Invalid enrollment for student",
        )
    
    grade = Grade(**grade_in.dict())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

# PUBLIC_INTERFACE
@router.get("/grades/{grade_id}", response_model=GradeSchema)
def get_grade(
    grade_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get grade by ID."""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade

# PUBLIC_INTERFACE
@router.put("/grades/{grade_id}", response_model=GradeSchema)
def update_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: str,
    grade_in: GradeUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update grade."""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    for field, value in grade_in.dict(exclude_unset=True).items():
        setattr(grade, field, value)
    
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

# PUBLIC_INTERFACE
@router.delete("/grades/{grade_id}", response_model=GradeSchema)
def delete_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete grade."""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    db.delete(grade)
    db.commit()
    return grade

# Attendance endpoints
# PUBLIC_INTERFACE
@router.get("/attendance/", response_model=List[AttendanceSchema])
def get_attendance_records(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get list of attendance records."""
    attendance_records = db.query(Attendance).offset(skip).limit(limit).all()
    return attendance_records

# PUBLIC_INTERFACE
@router.post("/attendance/", response_model=AttendanceSchema)
def create_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_in: AttendanceCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new attendance record."""
    # Verify enrollment exists and belongs to student
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == attendance_in.enrollment_id,
        Enrollment.student_id == attendance_in.student_id
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=400,
            detail="Invalid enrollment for student",
        )
    
    # Check for duplicate attendance record
    existing_attendance = db.query(Attendance).filter(
        Attendance.student_id == attendance_in.student_id,
        Attendance.enrollment_id == attendance_in.enrollment_id,
        Attendance.date == attendance_in.date
    ).first()
    
    if existing_attendance:
        raise HTTPException(
            status_code=400,
            detail="Attendance record already exists for this date",
        )
    
    attendance = Attendance(**attendance_in.dict())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

# PUBLIC_INTERFACE
@router.get("/attendance/{attendance_id}", response_model=AttendanceSchema)
def get_attendance(
    attendance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get attendance record by ID."""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance

# PUBLIC_INTERFACE
@router.put("/attendance/{attendance_id}", response_model=AttendanceSchema)
def update_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    attendance_in: AttendanceUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update attendance record."""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    for field, value in attendance_in.dict(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

# PUBLIC_INTERFACE
@router.delete("/attendance/{attendance_id}", response_model=AttendanceSchema)
def delete_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete attendance record."""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(attendance)
    db.commit()
    return attendance

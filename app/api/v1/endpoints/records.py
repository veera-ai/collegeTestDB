"""Records management endpoints for enrollments, grades and attendance."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    check_user_role,
    get_request
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
from app.services.audit import audit_service

router = APIRouter()

# Grade endpoints with audit logging
# PUBLIC_INTERFACE
@router.get("/grades/", response_model=List[GradeSchema])
def get_grades(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
    request: Request = Depends(get_request),
) -> Any:
    """Get list of grades."""
    grades = db.query(Grade).offset(skip).limit(limit).all()
    
    # Log grade list retrieval
    audit_service.log_activity(
        db=db,
        user=current_user,
        action="list",
        entity_type="grade",
        entity_id="all",
        request=request,
        details=f"Grade list retrieved by {current_user.username}"
    )
    
    return grades

# PUBLIC_INTERFACE
@router.post("/grades/", response_model=GradeSchema)
def create_grade(
    *,
    db: Session = Depends(get_db),
    grade_in: GradeCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
    request: Request = Depends(get_request),
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
    
    # Log grade creation
    audit_service.log_activity(
        db=db,
        user=current_user,
        action="create",
        entity_type="grade",
        entity_id=str(grade.id),
        changes=grade_in.dict(),
        request=request,
        details=f"Grade created for student ID: {grade_in.student_id} by {current_user.username}"
    )
    
    return grade

# PUBLIC_INTERFACE
@router.put("/grades/{grade_id}", response_model=GradeSchema)
def update_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: str,
    grade_in: GradeUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
    request: Request = Depends(get_request),
) -> Any:
    """Update grade."""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    original_grade = grade.grade_value
    changes = grade_in.dict(exclude_unset=True)
    
    for field, value in changes.items():
        setattr(grade, field, value)
    
    db.add(grade)
    db.commit()
    db.refresh(grade)
    
    # Log grade update
    audit_service.log_activity(
        db=db,
        user=current_user,
        action="update",
        entity_type="grade",
        entity_id=grade_id,
        changes={
            "previous_grade": original_grade,
            "new_grade": grade.grade_value,
            **changes
        },
        request=request,
        details=f"Grade updated for student ID: {grade.student_id} by {current_user.username}"
    )
    
    return grade

# PUBLIC_INTERFACE
@router.delete("/grades/{grade_id}", response_model=GradeSchema)
def delete_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
    request: Request = Depends(get_request),
) -> Any:
    """Delete grade."""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    student_id = grade.student_id
    grade_value = grade.grade_value
    db.delete(grade)
    db.commit()
    
    # Log grade deletion
    audit_service.log_activity(
        db=db,
        user=current_user,
        action="delete",
        entity_type="grade",
        entity_id=grade_id,
        changes={"deleted_grade": grade_value},
        request=request,
        details=f"Grade deleted for student ID: {student_id} by {current_user.username}"
    )
    
    return grade

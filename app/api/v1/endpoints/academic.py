"""Academic management endpoints for students and staff."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    check_user_role
)
from app.models.user import User, UserRole
from app.models.academic import Student, Staff
from app.schemas.academic import (
    Student as StudentSchema,
    StudentCreate,
    StudentUpdate,
    Staff as StaffSchema,
    StaffCreate,
    StaffUpdate
)

router = APIRouter()

# Student endpoints
# PUBLIC_INTERFACE
@router.get("/students/", response_model=List[StudentSchema])
def get_students(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get list of students."""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

# PUBLIC_INTERFACE
@router.post("/students/", response_model=StudentSchema)
def create_student(
    *,
    db: Session = Depends(get_db),
    student_in: StudentCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new student."""
    # Check if student with enrollment number exists
    student = db.query(Student).filter(
        Student.enrollment_number == student_in.enrollment_number
    ).first()
    if student:
        raise HTTPException(
            status_code=400,
            detail="A student with this enrollment number already exists.",
        )
    
    # Check if user_id exists and is not already assigned
    student = db.query(Student).filter(Student.user_id == student_in.user_id).first()
    if student:
        raise HTTPException(
            status_code=400,
            detail="This user is already assigned to a student profile.",
        )
    
    student = Student(**student_in.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

# PUBLIC_INTERFACE
@router.get("/students/{student_id}", response_model=StudentSchema)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get student by ID."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# PUBLIC_INTERFACE
@router.put("/students/{student_id}", response_model=StudentSchema)
def update_student(
    *,
    db: Session = Depends(get_db),
    student_id: str,
    student_in: StudentUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update student."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if enrollment number is being updated and is unique
    if student_in.enrollment_number is not None:
        existing_student = db.query(Student).filter(
            Student.enrollment_number == student_in.enrollment_number,
            Student.id != student_id
        ).first()
        if existing_student:
            raise HTTPException(
                status_code=400,
                detail="A student with this enrollment number already exists.",
            )
    
    for field, value in student_in.dict(exclude_unset=True).items():
        setattr(student, field, value)
    
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

# PUBLIC_INTERFACE
@router.delete("/students/{student_id}", response_model=StudentSchema)
def delete_student(
    *,
    db: Session = Depends(get_db),
    student_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete student."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return student

# Staff endpoints
# PUBLIC_INTERFACE
@router.get("/staff/", response_model=List[StaffSchema])
def get_staff_members(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Get list of staff members."""
    staff_members = db.query(Staff).offset(skip).limit(limit).all()
    return staff_members

# PUBLIC_INTERFACE
@router.post("/staff/", response_model=StaffSchema)
def create_staff_member(
    *,
    db: Session = Depends(get_db),
    staff_in: StaffCreate,
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Create new staff member."""
    # Check if staff with employee_id exists
    staff = db.query(Staff).filter(Staff.employee_id == staff_in.employee_id).first()
    if staff:
        raise HTTPException(
            status_code=400,
            detail="A staff member with this employee ID already exists.",
        )
    
    # Check if user_id exists and is not already assigned
    staff = db.query(Staff).filter(Staff.user_id == staff_in.user_id).first()
    if staff:
        raise HTTPException(
            status_code=400,
            detail="This user is already assigned to a staff profile.",
        )
    
    staff = Staff(**staff_in.dict())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

# PUBLIC_INTERFACE
@router.get("/staff/{staff_id}", response_model=StaffSchema)
def get_staff_member(
    staff_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Get staff member by ID."""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff

# PUBLIC_INTERFACE
@router.put("/staff/{staff_id}", response_model=StaffSchema)
def update_staff_member(
    *,
    db: Session = Depends(get_db),
    staff_id: str,
    staff_in: StaffUpdate,
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Update staff member."""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check if employee_id is being updated and is unique
    if staff_in.employee_id is not None:
        existing_staff = db.query(Staff).filter(
            Staff.employee_id == staff_in.employee_id,
            Staff.id != staff_id
        ).first()
        if existing_staff:
            raise HTTPException(
                status_code=400,
                detail="A staff member with this employee ID already exists.",
            )
    
    for field, value in staff_in.dict(exclude_unset=True).items():
        setattr(staff, field, value)
    
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

# PUBLIC_INTERFACE
@router.delete("/staff/{staff_id}", response_model=StaffSchema)
def delete_staff_member(
    *,
    db: Session = Depends(get_db),
    staff_id: str,
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Delete staff member."""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    db.delete(staff)
    db.commit()
    return staff

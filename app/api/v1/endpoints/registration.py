"""Registration and Report management endpoints."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    check_user_role
)
from app.models.user import User, UserRole
from app.models.registration import Registration, Report
from app.schemas.registration import (
    Registration as RegistrationSchema,
    RegistrationCreate,
    RegistrationUpdate,
    Report as ReportSchema,
    ReportCreate,
    ReportUpdate
)

router = APIRouter()

# Registration endpoints
# PUBLIC_INTERFACE
@router.get("/registrations/", response_model=List[RegistrationSchema])
def get_registrations(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get list of registrations."""
    # Regular users can only see their own registrations
    if current_user.role == UserRole.STUDENT:
        registrations = db.query(Registration).filter(
            Registration.user_id == current_user.id
        ).offset(skip).limit(limit).all()
    else:
        registrations = db.query(Registration).offset(skip).limit(limit).all()
    return registrations

# PUBLIC_INTERFACE
@router.post("/registrations/", response_model=RegistrationSchema)
def create_registration(
    *,
    db: Session = Depends(get_db),
    registration_in: RegistrationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create new registration."""
    # Check if registration already exists
    existing_registration = db.query(Registration).filter(
        Registration.event_id == registration_in.event_id,
        Registration.user_id == registration_in.user_id
    ).first()
    if existing_registration:
        raise HTTPException(
            status_code=400,
            detail="User is already registered for this event",
        )
    
    # Only allow users to register themselves or staff to register others
    if (registration_in.user_id != current_user.id and 
        current_user.role == UserRole.STUDENT):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to register other users"
        )
    
    registration = Registration(**registration_in.dict())
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration

# PUBLIC_INTERFACE
@router.get("/registrations/{registration_id}", response_model=RegistrationSchema)
def get_registration(
    registration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get registration by ID."""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if user has permission to view this registration
    if (current_user.role == UserRole.STUDENT and 
        registration.user_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this registration"
        )
    return registration

# PUBLIC_INTERFACE
@router.put("/registrations/{registration_id}", response_model=RegistrationSchema)
def update_registration(
    *,
    db: Session = Depends(get_db),
    registration_id: str,
    registration_in: RegistrationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update registration."""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Only allow users to update their own registration or staff to update any
    if (current_user.role == UserRole.STUDENT and 
        registration.user_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this registration"
        )
    
    for field, value in registration_in.dict(exclude_unset=True).items():
        setattr(registration, field, value)
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration

# PUBLIC_INTERFACE
@router.delete("/registrations/{registration_id}", response_model=RegistrationSchema)
def delete_registration(
    *,
    db: Session = Depends(get_db),
    registration_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete registration."""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Only allow users to delete their own registration or staff to delete any
    if (current_user.role == UserRole.STUDENT and 
        registration.user_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this registration"
        )
    
    db.delete(registration)
    db.commit()
    return registration

# Report endpoints
# PUBLIC_INTERFACE
@router.get("/reports/", response_model=List[ReportSchema])
def get_reports(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get list of reports."""
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports

# PUBLIC_INTERFACE
@router.post("/reports/", response_model=ReportSchema)
def create_report(
    *,
    db: Session = Depends(get_db),
    report_in: ReportCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new report."""
    report = Report(**report_in.dict())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

# PUBLIC_INTERFACE
@router.get("/reports/{report_id}", response_model=ReportSchema)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# PUBLIC_INTERFACE
@router.put("/reports/{report_id}", response_model=ReportSchema)
def update_report(
    *,
    db: Session = Depends(get_db),
    report_id: str,
    report_in: ReportUpdate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Update report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    for field, value in report_in.dict(exclude_unset=True).items():
        setattr(report, field, value)
    
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

# PUBLIC_INTERFACE
@router.delete("/reports/{report_id}", response_model=ReportSchema)
def delete_report(
    *,
    db: Session = Depends(get_db),
    report_id: str,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Delete report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return report

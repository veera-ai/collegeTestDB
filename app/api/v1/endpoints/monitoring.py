"""Monitoring endpoints for dashboards and audit logs."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    check_user_role
)
from app.models.user import User, UserRole
from app.models.monitoring import Dashboard, AuditLog
from app.schemas.monitoring import (
    Dashboard as DashboardSchema,
    DashboardCreate,
    DashboardUpdate,
    AuditLog as AuditLogSchema,
    AuditLogCreate,
    AuditLogUpdate
)

router = APIRouter()

# Dashboard endpoints
# PUBLIC_INTERFACE
@router.get("/dashboards/", response_model=List[DashboardSchema])
def get_dashboards(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get list of dashboards."""
    # Regular users can only see their own dashboards
    if current_user.role == UserRole.STUDENT:
        dashboards = db.query(Dashboard).filter(
            Dashboard.user_id == current_user.id
        ).offset(skip).limit(limit).all()
    else:
        dashboards = db.query(Dashboard).offset(skip).limit(limit).all()
    return dashboards

# PUBLIC_INTERFACE
@router.post("/dashboards/", response_model=DashboardSchema)
def create_dashboard(
    *,
    db: Session = Depends(get_db),
    dashboard_in: DashboardCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create new dashboard."""
    # Users can only create dashboards for themselves unless they are staff
    if (dashboard_in.user_id != current_user.id and 
        current_user.role == UserRole.STUDENT):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create dashboard for other users"
        )
    
    # Check if this is being set as default and handle accordingly
    if dashboard_in.is_default:
        # Remove default flag from other dashboards of this user
        existing_defaults = db.query(Dashboard).filter(
            Dashboard.user_id == dashboard_in.user_id,
            Dashboard.is_default == True
        ).all()
        for dash in existing_defaults:
            dash.is_default = False
            db.add(dash)
    
    dashboard = Dashboard(**dashboard_in.dict())
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard

# PUBLIC_INTERFACE
@router.get("/dashboards/{dashboard_id}", response_model=DashboardSchema)
def get_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get dashboard by ID."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Check if user has permission to view this dashboard
    if (current_user.role == UserRole.STUDENT and 
        dashboard.user_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this dashboard"
        )
    return dashboard

# PUBLIC_INTERFACE
@router.put("/dashboards/{dashboard_id}", response_model=DashboardSchema)
def update_dashboard(
    *,
    db: Session = Depends(get_db),
    dashboard_id: str,
    dashboard_in: DashboardUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Only allow users to update their own dashboard or staff to update any
    if (current_user.role == UserRole.STUDENT and 
        dashboard.user_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this dashboard"
        )
    
    # Handle default flag changes
    if dashboard_in.is_default and not dashboard.is_default:
        # Remove default flag from other dashboards of this user
        existing_defaults = db.query(Dashboard).filter(
            Dashboard.user_id == dashboard.user_id,
            Dashboard.is_default == True,
            Dashboard.id != dashboard_id
        ).all()
        for dash in existing_defaults:
            dash.is_default = False
            db.add(dash)
    
    for field, value in dashboard_in.dict(exclude_unset=True).items():
        setattr(dashboard, field, value)
    
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard

# PUBLIC_INTERFACE
@router.delete("/dashboards/{dashboard_id}", response_model=DashboardSchema)
def delete_dashboard(
    *,
    db: Session = Depends(get_db),
    dashboard_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete dashboard."""
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Only allow users to delete their own dashboard or staff to delete any
    if (current_user.role == UserRole.STUDENT and 
        dashboard.user_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this dashboard"
        )
    
    db.delete(dashboard)
    db.commit()
    return dashboard

# Audit Log endpoints
# PUBLIC_INTERFACE
@router.get("/audit-logs/", response_model=List[AuditLogSchema])
def get_audit_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get list of audit logs."""
    audit_logs = db.query(AuditLog).offset(skip).limit(limit).all()
    return audit_logs

# PUBLIC_INTERFACE
@router.post("/audit-logs/", response_model=AuditLogSchema)
def create_audit_log(
    *,
    db: Session = Depends(get_db),
    audit_log_in: AuditLogCreate,
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Create new audit log entry."""
    audit_log = AuditLog(**audit_log_in.dict())
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

# PUBLIC_INTERFACE
@router.get("/audit-logs/{audit_log_id}", response_model=AuditLogSchema)
def get_audit_log(
    audit_log_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role(UserRole.STAFF)),
) -> Any:
    """Get audit log entry by ID."""
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log entry not found")
    return audit_log

# PUBLIC_INTERFACE
@router.put("/audit-logs/{audit_log_id}", response_model=AuditLogSchema)
def update_audit_log(
    *,
    db: Session = Depends(get_db),
    audit_log_id: str,
    audit_log_in: AuditLogUpdate,
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Update audit log entry. Restricted to admin users only."""
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log entry not found")
    
    for field, value in audit_log_in.dict(exclude_unset=True).items():
        setattr(audit_log, field, value)
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

# PUBLIC_INTERFACE
@router.delete("/audit-logs/{audit_log_id}", response_model=AuditLogSchema)
def delete_audit_log(
    *,
    db: Session = Depends(get_db),
    audit_log_id: str,
    current_user: User = Depends(check_user_role(UserRole.ADMIN)),
) -> Any:
    """Delete audit log entry. Restricted to admin users only."""
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log entry not found")
    
    db.delete(audit_log)
    db.commit()
    return audit_log

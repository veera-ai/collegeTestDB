"""Audit logging service for tracking system activities."""
from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.monitoring import AuditLog
from app.models.user import User

class AuditService:
    """Service for handling audit logging."""

    @staticmethod
    def log_activity(
        db: Session,
        user: User,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        details: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry."""
        audit_log = AuditLog(
            user_id=user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            details=details
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

audit_service = AuditService()

"""Authentication endpoints."""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user, get_request
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.token import Token
from app.services.audit import audit_service

router = APIRouter()

# PUBLIC_INTERFACE
@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = Depends(get_request)
) -> Any:
    """Login endpoint for OAuth2 authentication."""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if user is None:
        # Log failed login attempt
        audit_service.log_activity(
            db=db,
            user=None,
            action="login_failed",
            entity_type="auth",
            entity_id=form_data.username,
            request=request,
            details=f"Failed login attempt for email: {form_data.username} (user not found)"
        )
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not security.verify_password(form_data.password, user.password_hash):
        # Log failed login attempt
        audit_service.log_activity(
            db=db,
            user=None,
            action="login_failed",
            entity_type="auth",
            entity_id=str(user.id),
            request=request,
            details=f"Failed login attempt for user: {user.username} (invalid password)"
        )
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        # Log inactive user attempt
        audit_service.log_activity(
            db=db,
            user=None,
            action="login_failed",
            entity_type="auth",
            entity_id=str(user.id),
            request=request,
            details=f"Failed login attempt for user: {user.username} (inactive user)"
        )
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Log successful login
    audit_service.log_activity(
        db=db,
        user=user,
        action="login_success",
        entity_type="auth",
        entity_id=str(user.id),
        request=request,
        details=f"Successful login for user: {user.username}"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# PUBLIC_INTERFACE
@router.post("/test-token", response_model=UserSchema)
def test_token(
    current_user: User = Depends(get_current_user),
    request: Request = Depends(get_request),
    db: Session = Depends(get_db)
) -> Any:
    """Test access token."""
    # Log token test
    audit_service.log_activity(
        db=db,
        user=current_user,
        action="token_test",
        entity_type="auth",
        entity_id=str(current_user.id),
        request=request,
        details=f"Token test performed by user: {current_user.username}"
    )
    return current_user

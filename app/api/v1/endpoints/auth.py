"""Authentication endpoints."""
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_user, get_request
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.token import Token
from app.services.audit import audit_service
from app.schemas.responses import HTTPError, HTTPValidationError

router = APIRouter()

# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {
            "description": "Successful login",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {
            "description": "Invalid credentials or inactive user",
            "model": HTTPError,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Invalid credentials",
                            "value": {"detail": "Incorrect email or password"}
                        },
                        "inactive_user": {
                            "summary": "Inactive user",
                            "value": {"detail": "Inactive user"}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation Error",
            "model": HTTPValidationError
        }
    }
)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = Depends(get_request)
) -> Any:
    """
    OAuth2 compatible token login.
    
    ## Description
    This endpoint authenticates a user and returns a JWT token for accessing protected endpoints.
    
    ## Parameters
    * **username**: Email address of the user
    * **password**: User's password
    
    ## Returns
    * **access_token**: JWT token for authentication
    * **token_type**: Type of token (always "bearer")
    
    ## Usage
    After obtaining the token, include it in the Authorization header of subsequent requests:
    `Authorization: Bearer <access_token>`
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if user is None:
        audit_service.log_activity(
            db=db,
            user=None,
            action="login_failed",
            entity_type="auth",
            entity_id=form_data.username,
            request=request,
            details=f"Failed login attempt for email: {form_data.username} (user not found)"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    if not security.verify_password(form_data.password, user.password_hash):
        audit_service.log_activity(
            db=db,
            user=None,
            action="login_failed",
            entity_type="auth",
            entity_id=str(user.id),
            request=request,
            details=f"Failed login attempt for user: {user.username} (invalid password)"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        audit_service.log_activity(
            db=db,
            user=None,
            action="login_failed",
            entity_type="auth",
            entity_id=str(user.id),
            request=request,
            details=f"Failed login attempt for user: {user.username} (inactive user)"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
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
@router.post(
    "/test-token",
    response_model=UserSchema,
    responses={
        200: {
            "description": "Token is valid",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "testuser",
                        "full_name": "Test User",
                        "role": "student",
                        "is_active": True,
                        "is_superuser": False
                    }
                }
            }
        },
        401: {
            "description": "Invalid or expired token",
            "model": HTTPError,
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def test_token(
    current_user: User = Depends(get_current_user),
    request: Request = Depends(get_request),
    db: Session = Depends(get_db)
) -> Any:
    """
    Test access token validity.
    
    ## Description
    This endpoint validates the provided JWT token and returns the user information if the token is valid.
    
    ## Authentication
    * Required: Bearer token in Authorization header
    
    ## Returns
    * User information if the token is valid
    """
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

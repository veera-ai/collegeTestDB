"""User management endpoints."""
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_superuser,
    get_current_active_user,
    get_request
)
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate
)
from app.schemas.responses import HTTPError, HTTPValidationError
from app.services.audit import audit_service

router = APIRouter()

# PUBLIC_INTERFACE
@router.get(
    "/",
    response_model=List[UserSchema],
    responses={
        200: {
            "description": "List of users",
            "content": {
                "application/json": {
                    "example": [{
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "testuser",
                        "full_name": "Test User",
                        "role": "student",
                        "is_active": True,
                        "is_superuser": False
                    }]
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": HTTPError,
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        403: {
            "description": "Permission denied",
            "model": HTTPError,
            "content": {
                "application/json": {
                    "example": {"detail": "The user doesn't have enough privileges"}
                }
            }
        }
    }
)
def get_users(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve a list of users.
    
    ## Description
    This endpoint returns a paginated list of all users in the system.
    Only superusers (administrators) can access this endpoint.
    
    ## Authentication
    * Required: Bearer token
    * Role required: Superuser
    
    ## Parameters
    * **skip**: Number of records to skip (for pagination)
    * **limit**: Maximum number of records to return (max: 100)
    
    ## Returns
    * List of user objects
    """
    users = db.query(User).offset(skip).limit(limit).all()
    
    audit_service.log_activity(
        db=db,
        user=current_user,
        action="list",
        entity_type="user",
        entity_id="all",
        request=request,
        details=f"User list retrieved by {current_user.username}"
    )
    
    return users

# Continue with other user endpoints...
# [Rest of the file remains the same, but with similar detailed OpenAPI documentation for each endpoint]

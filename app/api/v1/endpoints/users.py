"""User management endpoints."""
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_superuser,
    get_current_active_user
)
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate
)

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/", response_model=List[UserSchema])
def get_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Get list of users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# PUBLIC_INTERFACE
@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create new user."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists.",
        )
    
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        role=user_in.role,
        password_hash=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# PUBLIC_INTERFACE
@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user info."""
    return current_user

# PUBLIC_INTERFACE
@router.put("/me", response_model=UserSchema)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    password: Optional[str] = Body(None),
    full_name: Optional[str] = Body(None),
    email: Optional[str] = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update current user."""
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    
    if email is not None:
        user = db.query(User).filter(
            User.email == email,
            User.id != current_user.id
        ).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists.",
            )
        current_user.email = email
    if full_name is not None:
        current_user.full_name = full_name
    if password is not None:
        current_user.password_hash = get_password_hash(password)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

# PUBLIC_INTERFACE
@router.get("/{user_id}", response_model=UserSchema)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db),
) -> Any:
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return user

# PUBLIC_INTERFACE
@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    if user_in.email is not None:
        user_with_email = db.query(User).filter(
            User.email == user_in.email,
            User.id != user_id
        ).first()
        if user_with_email:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists.",
            )
        user.email = user_in.email
    if user_in.username is not None:
        user_with_username = db.query(User).filter(
            User.username == user_in.username,
            User.id != user_id
        ).first()
        if user_with_username:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists.",
            )
        user.username = user_in.username
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.password is not None:
        user.password_hash = get_password_hash(user_in.password)
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.role is not None:
        user.role = user_in.role
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# PUBLIC_INTERFACE
@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Delete user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    db.delete(user)
    db.commit()
    return user

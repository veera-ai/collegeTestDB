from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr
from uuid import UUID
from app.models.user import UserRole
from app.schemas.base import BaseSchema

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(UserBase):
    password: Optional[constr(min_length=8)] = None

class UserInDBBase(UserBase, BaseSchema):
    id: UUID

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password_hash: str

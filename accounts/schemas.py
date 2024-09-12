from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from common.constants import RoleName


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone: Optional[str]
    first_name: str
    last_name: str
    super_user: bool
    roles: List[str] = []

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: RoleName


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    id: int

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    access_level: str


class PermissionCreate(PermissionBase):
    pass


class PermissionOut(PermissionBase):
    id: int

    class Config:
        from_attributes = True


class UserRoleOut(BaseModel):
    user_id: int
    role_id: int

    class Config:
        from_attributes = True


class TokenBase(BaseModel):
    token: str

class TokenCreate(TokenBase):
    pass


class TokenOut(BaseModel):
    token: str

    class Config:
        from_attributes = True

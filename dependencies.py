from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from functools import wraps

from accounts.models import User
from common.constants import PermissionName
from database import get_db
from accounts.routes import get_current_user
from security.permissions import has_permission


def permission_required(permission: PermissionName):
    def dependency(
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)
    ):
        if not has_permission(current_user, permission, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return True

    return dependency

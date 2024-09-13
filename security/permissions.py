from sqlalchemy import select
from sqlalchemy.orm import Session
from accounts.models import User, Permission, UserRole, RolePermission
from common.constants import PermissionName

def has_permission(user: User, permission_name: PermissionName, db: Session) -> bool:
    user_roles = db.execute(
        select(UserRole).where(UserRole.user_id == user.id)
    ).scalars().all()

    for user_role in user_roles:
        role_permissions = db.execute(
            select(RolePermission).where(RolePermission.role_id == user_role.role_id)
        ).scalars().all()

        for role_permission in role_permissions:
            permission = db.execute(
                select(Permission).where(Permission.id == role_permission.permission_id)
            ).scalars().first()

            if permission and permission.access_level == permission_name:
                return True
    return False

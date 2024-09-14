from typing import Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from accounts.models import Permission, Role, RolePermission
from common.constants import PermissionName, RoleName



def initialize_permissions(db: Session):
    # Define the required roles and permissions
    required_roles = [RoleName.ADMIN, RoleName.MANAGER, RoleName.USER]
    required_permissions = [
        PermissionName.CREATE_TASK,
        PermissionName.UPDATE_TASK,
        PermissionName.DELETE_TASK,
        PermissionName.READ_TASK
    ]

    # Ensure all required roles exist
    roles = get_or_create_roles(db, required_roles)

    # Ensure all required permissions exist
    permissions = get_or_create_permissions(db, required_permissions)

    # Assign permissions to ADMIN and MANAGER roles
    assign_permissions_to_roles(db, roles, permissions,
                                roles_to_assign=[RoleName.ADMIN,
                                                  RoleName.MANAGER])

    # Assign only READ_TASK permission to USER role
    assign_permissions_to_roles(db, roles, permissions,
                                roles_to_assign=[RoleName.USER],
                                permissions_to_assign=[
                                     PermissionName.READ_TASK])

    # Commit all changes to the database
    db.commit()


def get_or_create_roles(db: Session, required_roles: list) -> Dict[
    RoleName, Role]:
    # Fetch existing roles from the database
    existing_roles = db.query(Role).filter(Role.name.in_(required_roles)).all()
    existing_role_names = {role.name for role in existing_roles}

    # Create any missing roles
    for role_name in required_roles:
        if role_name not in existing_role_names:
            new_role = Role(name=role_name)
            db.add(new_role)
            existing_roles.append(new_role)

    # Refresh session to include newly added roles
    db.flush()

    # Create a dictionary of roles for easy access
    roles = {role.name: role for role in existing_roles}
    return roles


def get_or_create_permissions(db: Session, required_permissions: list) -> Dict[
    PermissionName, Permission]:
    # Fetch existing permissions from the database
    existing_permissions = db.query(Permission).filter(
        Permission.access_level.in_(required_permissions)).all()
    existing_permission_levels = {perm.access_level for perm in
                                  existing_permissions}

    # Create any missing permissions
    for permission_level in required_permissions:
        if permission_level not in existing_permission_levels:
            new_permission = Permission(access_level=permission_level)
            db.add(new_permission)
            existing_permissions.append(new_permission)

    # Refresh session to include newly added permissions
    db.flush()

    # Create a dictionary of permissions for easy access
    permissions = {perm.access_level: perm for perm in existing_permissions}
    return permissions


def assign_permissions_to_roles(
        db: Session,
        roles: Dict[RoleName, Role],
        permissions: Dict[PermissionName, Permission],
        roles_to_assign: list,
        permissions_to_assign: list = None
):

    if permissions_to_assign is None:
        # If no specific permissions are provided, assign all permissions
        permissions_to_assign = list(permissions.keys())

    for role_name in roles_to_assign:
        role = roles.get(role_name)
        if not role:
            continue  # Skip if the role does not exist

        for permission_name in permissions_to_assign:
            permission = permissions.get(permission_name)
            if not permission:
                continue  # Skip if the permission does not exist

            # Check if the role-permission association already exists
            association_exists = db.query(RolePermission).filter_by(
                role_id=role.id,
                permission_id=permission.id
            ).first()

            if not association_exists:
                # Create the association if it does not exist
                role_permission = RolePermission(role_id=role.id,
                                                 permission_id=permission.id)
                db.add(role_permission)
from enum import Enum


class RoleName(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

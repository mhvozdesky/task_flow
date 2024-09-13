from enum import Enum


class RoleName(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "In progress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PermissionName(str, Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    READ_TASK = "read_task"

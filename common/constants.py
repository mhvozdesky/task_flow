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

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

from common.constants import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    responsible_id: int
    executor_ids: List[int] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    responsible_id: Optional[int] = None
    executor_ids: Optional[List[int]] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    responsible_id: int
    executor_ids: List[int]

    class Config:
        from_attributes = True

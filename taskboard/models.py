from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, \
    UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from accounts.models import User
from common.constants import TaskStatus, TaskPriority


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    responsible_id = Column(Integer, ForeignKey("users.id"))

    responsible = relationship("User", back_populates="tasks_responsible")
    executors = relationship("User", secondary="task_executors")


class TaskExecutors(Base):
    __tablename__ = "task_executors"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint('task_id', 'user_id', name='_task_user_uc'),
    )

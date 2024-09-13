from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, \
    UniqueConstraint, event, inspect
from sqlalchemy.orm import relationship
from database import Base
from accounts.models import User
from common.constants import TaskStatus, TaskPriority
from email_notification.email_sender import send_email


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


def after_update_listener(mapper, connection, target):
    state = inspect(target)
    history = state.attrs.status.history
    if history.has_changes():
        old_status = history.deleted[0] if history.deleted else None
        new_status = history.added[0] if history.added else None
        if new_status and new_status != old_status:
            if target.responsible:
                subject = f"Статус задачі '{target.title}' змінився на {target.status.value}"
                body = f"Ваша задача '{target.title}' зараз має статус: {target.status.value}."

                send_email(target.responsible.email, subject, body)

event.listen(Task, 'after_update', after_update_listener)

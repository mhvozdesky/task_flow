from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from starlette import status

from .schemas import TaskCreate, TaskUpdate, TaskOut
from .models import Task, TaskExecutors
from accounts.models import User
from database import get_db
from typing import List, Set, Optional

router = APIRouter()


def get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.execute(select(Task).where(Task.id == task_id)).scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def validate_and_get_users(executor_ids: Set[int], db: Session) -> List[User]:
    existing_users = db.execute(
        select(User).where(User.id.in_(executor_ids))
    ).scalars().all()
    return existing_users


def validate_responsible_user(responsible_id: int, db: Session) -> User:
    user = db.execute(select(User).where(User.id == responsible_id)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Responsible user with ID {responsible_id} not found."
        )
    return user


def assign_executors(task: Task, executor_ids: Optional[List[int]], db: Session):
    if executor_ids is not None:
        unique_executor_ids = set(executor_ids)
        users = validate_and_get_users(unique_executor_ids, db)

        db.execute(delete(TaskExecutors).where(TaskExecutors.task_id == task.id))

        task_executors = [
            TaskExecutors(task_id=task.id, user_id=user.id)
            for user in users
        ]
        db.bulk_save_objects(task_executors)
        db.commit()


@router.get("/tasks", response_model=List[TaskOut])
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.execute(select(Task)).scalars().all()

    tasks_with_executors = []
    for task in tasks:
        executor_ids = [executor.id for executor in task.executors]
        task.executor_ids = executor_ids
        tasks_with_executors.append(task)
    return tasks_with_executors


@router.post("/tasks", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    validate_responsible_user(task.responsible_id, db)

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        responsible_id=task.responsible_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    assign_executors(new_task, task.executor_ids, db)

    executor_ids = [executors.id for executors in new_task.executors]
    new_task.executor_ids = executor_ids
    return new_task


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)
    executor_ids = [executor.id for executor in task.executors]
    task.executor_ids = executor_ids
    return task


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate,
                db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)

    update_data = task_update.model_dump(exclude_unset=True)

    if "responsible_id" in update_data:
        validate_responsible_user(update_data["responsible_id"], db)

    for field, value in update_data.items():
        if field != "executor_ids":
            setattr(task, field, value)

    if "executor_ids" in update_data:
        assign_executors(task, task_update.executor_ids, db)

    db.commit()
    db.refresh(task)

    executor_ids = [executor.id for executor in task.executors]
    task.executor_ids = executor_ids
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)
    db.execute(delete(TaskExecutors).where(TaskExecutors.task_id == task_id))
    db.delete(task)
    db.commit()
    return {"msg": "Task deleted"}

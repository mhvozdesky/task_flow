from sqlalchemy import select

import pytest

from accounts.models import Role, UserRole
from accounts.routes import get_password_hash
from common.constants import RoleName
from taskboard.models import Task, User, TaskStatus, TaskPriority
from scripts.initialize_permissions import initialize_permissions

# Function for creating test tasks
def create_test_task(db_session, title, description, status, priority, responsible_user):
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        responsible_id=responsible_user.id
    )
    db_session.add(task)
    db_session.commit()
    return task


def create_test_user(db_session, email, password, role_name):
    hashed_password = get_password_hash(password)
    role = db_session.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db_session.add(role)
        db_session.commit()

    user = User(
        email=email,
        password=hashed_password,
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_role = db_session.query(Role).filter(Role.name == role_name).first()
    ur = UserRole(user_id=user.id, role_id=user_role.id)
    db_session.add(ur)
    db_session.commit()


def test_get_all_tasks(client, db_session):
    test_user = User(
        email="testuser@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    db_session.add(test_user)
    db_session.commit()

    create_test_task(db_session, "Task 1", "Description 1", TaskStatus.TODO, TaskPriority.HIGH, test_user)
    create_test_task(db_session, "Task 2", "Description 2", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, test_user)
    create_test_task(db_session, "Task 3", "Description 3", TaskStatus.DONE, TaskPriority.LOW, test_user)

    response = client.get("/taskboard/tasks")

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 3

    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"
    assert tasks[2]["title"] == "Task 3"


def test_get_tasks_pagination(client, db_session):
    test_user = User(
        email="testuser2@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    db_session.add(test_user)
    db_session.commit()

    for i in range(5):
        create_test_task(db_session, f"Task {i+1}", f"Description {i+1}", TaskStatus.TODO, TaskPriority.HIGH, test_user)

    response = client.get("/taskboard/tasks?page=1&page_size=2")
    assert response.status_code == 200
    tasks = response.json()

    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"

    assert response.headers["X-Total-Count"] == "5"
    assert response.headers["X-Total-Pages"] == "3"
    assert response.headers["X-Current-Page"] == "1"
    assert response.headers["X-Page-Size"] == "2"

    response = client.get("/taskboard/tasks?page=2&page_size=2")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 3"
    assert tasks[1]["title"] == "Task 4"

    response = client.get("/taskboard/tasks?page=3&page_size=2")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task 5"


def test_get_tasks_ordering(client, db_session):
    test_user = User(
        email="testuser3@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    db_session.add(test_user)
    db_session.commit()

    create_test_task(db_session, "Task A", "Description A", TaskStatus.TODO, TaskPriority.HIGH, test_user)
    create_test_task(db_session, "Task C", "Description C", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, test_user)
    create_test_task(db_session, "Task B", "Description B", TaskStatus.DONE, TaskPriority.LOW, test_user)

    response = client.get("/taskboard/tasks?order_by=-title")
    assert response.status_code == 200
    tasks = response.json()

    assert tasks[0]["title"] == "Task C"
    assert tasks[1]["title"] == "Task B"
    assert tasks[2]["title"] == "Task A"


def test_create_task_success(client, db_session):
    create_test_user(db_session, "admin@example.com", "password123", RoleName.ADMIN)
    initialize_permissions(db_session)
    test_user = db_session.execute(
        select(User).where(User.email == 'admin@example.com')
    ).scalars().first()

    login_data = {
        "email": "admin@example.com",
        "password": "password123"
    }
    login_response = client.post("accounts/login", json=login_data)
    assert login_response.status_code == 200
    resp = login_response.json()
    token = resp["token"]

    task_data = {
        "title": "New Task",
        "description": "Task Description",
        "status": TaskStatus.TODO,
        "priority": TaskPriority.HIGH,
        "responsible_id": test_user.id,
        "executor_ids": [test_user.id]
    }

    response = client.post(
        "/taskboard/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    task = response.json()
    assert task["title"] == "New Task"
    assert task["description"] == "Task Description"
    assert task["status"] == TaskStatus.TODO
    assert task["priority"] == TaskPriority.HIGH
    assert task["responsible_id"] == test_user.id
    assert task["executor_ids"] == [test_user.id]


def test_create_task_no_permission(client, db_session):
    create_test_user(db_session, "user@example.com", "password123", RoleName.USER)
    test_user = db_session.execute(
        select(User).where(User.email == 'user@example.com')
    ).scalars().first()

    login_data = {
        "email": "user@example.com",
        "password": "password123"
    }
    login_response = client.post("/accounts/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["token"]

    task_data = {
        "title": "New Task",
        "description": "Task Description",
        "status": TaskStatus.TODO,
        "priority": TaskPriority.HIGH,
        "responsible_id": test_user.id,
        "executor_ids": [test_user.id]
    }

    response = client.post(
        "/taskboard/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}

import pytest
from sqlalchemy import select

from accounts.models import User, Role, RoleName
from accounts.routes import get_password_hash


def test_register_new_user(client, db_session):
    new_user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "phone": "1234567890",
        "first_name": "Test",
        "last_name": "User"
    }

    response = client.post("/accounts/register", json=new_user_data)

    assert response.status_code == 200
    assert "token" in response.json()

    user_in_db = db_session.execute(
        select(User).where(User.email == new_user_data["email"])
    ).scalars().first()

    assert user_in_db is not None
    assert user_in_db.email == new_user_data["email"]


def test_register_existing_user(client, db_session):
    existing_user_data = {
        "email": "existinguser@example.com",
        "password": "password123",
        "phone": "1234567890",
        "first_name": "Existing",
        "last_name": "User"
    }

    client.post("accounts/register", json=existing_user_data)

    response = client.post("/accounts/register", json=existing_user_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_login_success(client, db_session):
    hashed_password = get_password_hash("password123")
    test_user = User(
        email="testuser@example.com",
        password=hashed_password,
        first_name="Test",
        last_name="User"
    )
    db_session.add(test_user)
    db_session.commit()

    login_data = {
        "email": "testuser@example.com",
        "password": "password123"
    }

    response = client.post("/accounts/login", json=login_data)

    assert response.status_code == 200
    json_response = response.json()
    assert "token" in json_response
    assert len(json_response["token"]) == 32


def test_login_invalid_email(client):
    login_data = {
        "email": "wrongemail@example.com",
        "password": "password123"
    }

    response = client.post("/accounts/login", json=login_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_invalid_password(client, db_session):
    hashed_password = get_password_hash("password123")
    test_user = User(
        email="testuser2@example.com",
        password=hashed_password,
        first_name="Test",
        last_name="User"
    )
    db_session.add(test_user)
    db_session.commit()

    login_data = {
        "email": "testuser2@example.com",
        "password": "wrongpassword"
    }

    response = client.post("/accounts/login", json=login_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

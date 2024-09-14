import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """A database fixture that cleans all data before each test."""
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection, expire_on_commit=False)
    Base.metadata.create_all(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI client fixture with test database."""
    def get_db_override():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = get_db_override
    with TestClient(app) as client:
        yield client

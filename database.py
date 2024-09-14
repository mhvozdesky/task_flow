from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from settings import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    DB_HOST,
    DB_PORT,
    POSTGRES_DB
)


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

from database import engine, Base
from accounts.routes import router as accounts_router
from scripts.initialize_permissions import initialize_permissions
from taskboard.routes import router as tasks_router
from database import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # logic when starting app
    db: Session = next(get_db())
    initialize_permissions(db)
    yield
    # Here we can add logic to terminate the application (if required)


app = FastAPI(lifespan=lifespan)

app.include_router(accounts_router, prefix='/accounts')
app.include_router(tasks_router, prefix='/taskboard')


@app.get("/")
async def read_root():
    return {"message": "TaskFlow backend is running!"}

from fastapi import FastAPI

from database import engine, Base
from accounts.routes import router as accounts_router
from taskboard.routes import router as tasks_router


app = FastAPI()

app.include_router(accounts_router, prefix='/accounts')
app.include_router(tasks_router, prefix='/taskboard')

@app.get("/")
async def read_root():
    return {"message": "TaskFlow backend is running!"}

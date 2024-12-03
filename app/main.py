from fastapi import FastAPI
from app.api import group, user
from app.core.database import initialize_database

initialize_database()

app = FastAPI()

app.include_router(user.router)
app.include_router(group.router)

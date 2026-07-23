from fastapi import FastAPI
from app.routers.users_router import users_router
from app.routers.auth_router import auth_router
from app.security import user_auth
from contextlib import asynccontextmanager
from app.db.db_handler import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="SO CALLS AUTOMATION", lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)

@app.get("/")
async def default():
    return {"Hello, World!"}

@app.get("/health/")
async def get_state(service_name: str):
    return "Great"

@app.post("/transcripts/")
async def add_transcript(transcript: list[str]):
    return "success"
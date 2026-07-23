from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.mango_router import mango_router
from app.db.db_handler import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="SO CALLS AUTOMATION", lifespan=lifespan)

app.include_router(mango_router)
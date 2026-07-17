from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.mango_router import mango_router
from app.db.db_handler import create_db_and_tables
from app.messaging.kafka_topics import create_kafka_topics

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    create_kafka_topics()
    yield

app = FastAPI(title="SO CALLS AUTOMATION", lifespan=lifespan)

app.include_router(mango_router)
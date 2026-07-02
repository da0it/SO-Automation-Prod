from fastapi import FastAPI
from backend.routers import users_router

app = FastAPI()

@app.include_router(users_router)

@app.get("/")
async def default():
    return {"Hello, World!"}

@app.get("/health/")
async def get_state(service_name: str):
    return "Great"

@app.post("/transcripts/")
async def add_transcript(transcript: list[str]):
    return "success"
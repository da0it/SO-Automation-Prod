from datetime import datetime
from typing import Any
from enum import Enum
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from dotenv import load_dotenv
import os,json

load_dotenv()

class RecordingState(str, Enum):
    STARTED="started"
    CONTINUED="continued"
    COMPLETED="completed"

class TranscriptState(str, Enum):
    PENDING="pending"
    NOT_READY="not ready"
    READY="ready"
    FAILED="failed"

class RecordingState(str, Enum):
    READY="ready"
    PENDING="pending"
    NOT_RECORDED="not recorded"
    FAILED="failed"

class EntryResult(int, Enum):
    FAILURE=0
    SUCCESS=1

class MangoCalls(SQLModel, table=True):
    __tablename__="mango_calls"

    id: str = Field(primary_key=True)
    entry_id: str | None = None
    sip_call_id: str
    entry_result: int = Field(default=None)
    recording_state: str = Field(default=RecordingState.NOT_RECORDED)
    recording_id: str | None = None
    transcript_status: str = Field(default=TranscriptState.NOT_READY)
    created_at: datetime
    updated_at: datetime = Field(default=None)

class CallTranscript(MangoCalls):
    transcript_result: str
    names: dict[str, Any] | None = None
    phrases: dict[str, Any] | None = None
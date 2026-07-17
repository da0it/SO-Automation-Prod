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
    NOT_READY="not ready"
    READY="ready"
    FAILED="failed"

class EntryResult(str, Enum):
    FAILURE=0
    SUCCESS=1

class MangoCalls(SQLModel, table=True):
    __tablename__="mango_calls"

    id: str = Field(primary_key=True)
    entry_id: str | None = None
    sip_call_id: str
    entry_result: int = Field(default=EntryResult.FAILURE)
    # line_number: str = Field(default=os.getenv('DEFAULT_SUPPORT_LINE_NUMBER'))
    recording_ready: bool | False = False
    recording_id: str | None = None
    transcript_ready: bool | False = False
    created_at: datetime
    updated_at: datetime = Field(default=None)

class CallTranscript(MangoCalls):
    transcript_result: str
    names: dict[str, Any] | None = None
    phrases: dict[str, Any] | None = None
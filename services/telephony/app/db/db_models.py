from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
import json



class CallState(str, Enum):
    APPEARED="appeared"
    CONNECTED="connected"
    ON_HOLD="on hold"
    DISCONNECTED="disconnected"

class RecordingState(str, Enum):
    STARTED="started"
    CONTINUED="continued"
    COMPLETED="completed"

class MangoCalls(SQLModel, table=True):
    __tablename__="mango_calls"

    id: str = Field(primary_key=True)
    created_at: datetime
    updated_at: datetime = Field(default=None)
    line_number: str = Field(default=2)
    client_phone_hash: str | None = None
    client_phone_masked: str | None = None
    call_state: str
    sip_call_id: str | None = None

class CallRecording(SQLModel):
    id: str
    recording_state: str
    completion_code: str
    timestamp: datetime

# class Transcripts(SQLModel):
#     id: int
#     call_id: str
#     content: json
#     recieved_at: datetime
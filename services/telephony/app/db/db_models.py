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

class BaseCall(SQLModel):
    id: str
    start_time: datetime
    end_time: datetime

class Calls(BaseCall, table=True):
    __tablename__="calls"

    client_phone_hash: str
    client_phone_masked: str
    line_number: str
    call_state: str

class CallRecording(BaseCall):
    id: str
    recording_state: str
    completion_code: str
    timestamp: datetime
    ai_summary: list[str]

class Transcripts(SQLModel):
    id: int
    call_id: str
    content: json
    recieved_at: datetime
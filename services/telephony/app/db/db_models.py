from datetime import datetime
from typing import Any
from enum import Enum
from sqlmodel import SQLModel, Field
import json
from dotenv import load_dotenv
import os

load_dotenv()

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
    line_number: str = Field(default=os.getenv('DEFAULT_SUPPORT_LINE_NUMBER'))
    client_phone_hash: str | None = None
    client_phone_masked: str | None = None
    recording_state: RecordingState = Field(default=RecordingState.STARTED)
    call_state: CallState
    sip_call_id: str | None = None

class CallTranscript(MangoCalls):
    transcript_result: str
    names: dict[str, Any] | None = None
    phrases: dict[str, Any] | None = None
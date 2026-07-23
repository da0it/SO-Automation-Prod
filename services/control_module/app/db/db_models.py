from sqlmodel import Field, SQLModel
from datetime import datetime
from enum import Enum

## 
## USER RELATED MODELS
##

class State(str, Enum):
    ACTIVE="active"
    DEACTIVATED="deactivated"
    PENDING="pending"

class Role(str, Enum):
    ADMIN="admin"
    OPERATOR="operator"

class UserBase(SQLModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int | None = None
    state: State
    role: Role
    created_at: datetime | None = None
    updated_at: datetime | None = None

class Users(UserBase, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    state: State = Field(default=State.PENDING)
    role: Role = Field(default=Role.OPERATOR)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

##
## AUTH TOKEN
##

class AuthToken(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None

##
## TICKET RELATED MODELS
##

class Priority(str, Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    EMERGENCY="emergency"

class Requests(SQLModel,table=True):
    __tablename__ = "requests"

    id: str = Field(primary_key=True)
    ticket_id: str 
    call_id: str | None = Field(default=None)
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    priority: Priority = Field(default=Priority.LOW)
    assignee_id: int | None = Field(default=None, foreign_key="users.id")
    intent_id: str | None = Field (default=None)
    intent_confidence: float | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

##
## AUDIT STORAGE
##

class AuditJournal(SQLModel,table=True):
    id: str = Field(primary_key=True)
    request_id: str = Field(foreign_key="requests.id")
    user_id: int | None = Field(default=None, foreign_key="users.id")
    action_type: str | None = Field(default=None)
    result: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
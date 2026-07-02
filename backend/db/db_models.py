from sqlmodel import Field, SQLModel, Column, JSON
from datetime import datetime
from typing import Literal
from enum import Enum

## 
## USER RELATED MODELS
##

class State(Enum):
    ACTIVE="active"
    DEACTIVATED="deactivated"
    PENDING="pending"

class Role(Enum):
    ADMIN="admin"
    OPERATOR="operator"

class UserBase(SQLModel):
    name: str
    email: str
    state: State = Field(default=State.PENDING)
    role: Role = Field(default=Role.OPERATOR)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

class Users(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


##
## TICKET RELATED MODELS
##

Priority = Literal["low", "medium", "high", "critical"]

class Requests(SQLModel,table=True):
    id: str = Field(primary_key=True)
    ticket_id: str 
    call_id: str | None = Field(default=None)
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    priority: Priority = Field(default="low")
    assignee_id: str | None = Field(default=None, foreign_key="users.id")
    intent_id: str | None = Field (default=None)
    intent_confidence: float | None = Field(default=None)
    created_at: datetime = Field(default=datetime.now)
    updated_at: datetime = Field(default=datetime.now)

##
## AUDIT STORAGE
##

class AuditJournal(SQLModel,table=True):
    id: str = Field(primary_key=True)
    request_id: str = Field(foreign_key="requests.id")
    user_id: str | None = Field(default=None, foreign_key="users.id")
    action_type: str | None = Field(default=None)
    result: str | None = Field(default=None)
    created_at: datetime = Field(default=datetime.now)
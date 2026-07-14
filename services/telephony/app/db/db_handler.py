from typing import Annotated, Any
from datetime import datetime, timezone

import os
import json

from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel, select

from app.db.db_models import MangoCalls, RecordingState

engine = create_engine(os.getenv('SQLALCHEMY_TELEFONY_DATABASE_URL'))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

class CallNotFoundForRecording(Exception):
    pass

def get_call_by_sip_call_id(sip_call_id: str, session: SessionDep) -> MangoCalls | None:
    return session.exec(
        select(MangoCalls).where(
            MangoCalls.sip_call_id == sip_call_id
        )
    ).one_or_none()

def get_call_by_entry_id(entry_id: str, session: SessionDep) -> MangoCalls | None:
    return session.exec(
        select(MangoCalls).where(
            MangoCalls.entry_id == entry_id
        )
    ).one_or_none()

##
## CALL EVENT RELATED FUNCTIONS
##

def handle_call_event_bd(payload: dict[str, Any], session: SessionDep):
    call = get_call_by_entry_id(payload["entry_id"], session)
    if call is not None:
       return update_existing_call_db(call, payload, session)
    else: 
        return create_call_db(payload, session)

def create_call_db(payload: dict[str, Any], session: SessionDep) -> MangoCalls:
    db_call = MangoCalls.model_validate(payload)
    session.add(db_call)
    session.commit()
    session.refresh(db_call)
    
    return db_call

def update_existing_call_db(call: MangoCalls,
                            payload: dict[str, Any] | None,
                            params: dict[str, Any] | None,
                            session: SessionDep) -> MangoCalls:
    if payload is None and params:
        for field_name, new_value in params:
            old_value = getattr(call, field_name, None)
            
            if old_value != new_value:
                setattr(call, field_name, new_value)
    else:
        update_data = MangoCalls.model_validate(payload).model_dump(exclude_unset=True,exclude={"id"})
        for field_name, new_value in update_data.items():
            old_value = getattr(call, field_name, None)

            if old_value != new_value:
                    setattr(call, field_name, new_value)
    
    call.updated_at = datetime.now(timezone.utc)

    session.add(call)
    session.commit()
    session.refresh(call)
    
    return call

##
## RECORDING EVENTS RELATED FUNCTIONS
##

def handle_record_added_event_db(payload: dict[str, Any], session: SessionDep) -> MangoCalls:
    db_call = get_call_by_entry_id(payload["entry_id"], session)

    if db_call is None:
        raise CallNotFoundForRecording
    
    db_call.recording_ready = True
    db_call.recording_id = payload["recording_id"]

    session.add(db_call)
    session.commit()
    session.refresh(db_call)

    return db_call
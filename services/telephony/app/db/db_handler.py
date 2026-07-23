from typing import Annotated, Any
from datetime import datetime, timezone

import os
import json

from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel, select

from app.db.db_models import MangoCalls, RecordingState, AiAnalysisState

engine = create_engine(os.getenv('SQLALCHEMY_TELEFONY_DATABASE_URL'))

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

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
       return update_existing_call_db(call, session, payload)
    else: 
        return create_call_db(payload, session)

def create_call_db(payload: dict[str, Any], session: SessionDep) -> MangoCalls:
    db_call = MangoCalls.model_validate(payload)
    session.add(db_call)
    session.commit()
    session.refresh(db_call)
    
    return db_call

def update_existing_call_db(call: MangoCalls,
                            session: SessionDep,
                            payload: dict[str, Any] | None,
                            params: dict[str, Any] = None) -> MangoCalls:
    update_data: dict[str, Any] = {}

    if payload is not None:
        update_data.update(
            MangoCalls.model_validate(payload).
            model_dump(exclude_unset=True, exclude={"id"})
        )
    
    if params is not None:
        update_data.update(params)

    for field_name, new_value in update_data.items():
        old_value = getattr(call, field_name, None)

        if old_value != new_value:
            setattr(call, field_name, new_value)

    
    call.updated_at = datetime.now(timezone.utc)

    session.add(call)
    session.commit()
    session.refresh(call)
    
    return call

def handle_summary_event_db(payload: dict[str, Any] | None,
                            session: SessionDep) -> MangoCalls:
    db_call = get_call_by_entry_id(payload["entry_id"], session)
    if db_call is not None: 
        try:
            call_final_state = payload["entry_result"]
        
            db_call.entry_result = call_final_state

            session.add(db_call)
            session.commit()
            session.refresh(db_call)
        except Exception as e:
            raise print(e)
    return db_call

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


## 
## AI ANALYSIS STATE
##
def update_ai_analysis_state_db(payload: dict[str, Any], session: SessionDep) -> MangoCalls:
    db_call = get_call_by_entry_id(payload["entry_id"], session)

    if db_call is None:
        raise CallNotFoundForRecording
    
    db_call.ai_analysis_state = AiAnalysisState(payload["state"])

    session.add(db_call)
    session.commit()
    session.refresh(db_call)

    return db_call
from dotenv import load_dotenv
from fastapi import Depends, HTTPException

from backend.db.db_models import Users, Requests
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

from typing import Annotated

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

##
## USER RELATED OPERATIONS
##

def create_user_db(user: Users,session: SessionDep) -> str:
    try:
        db_user = Users.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return "Success"
    except Exception:
        session.rollback()
        raise

def read_user_db(session: SessionDep):
    statement = select(Users)
    results = session.exec(statement)
    return results

def deactivate_user_db(user_id: str,session:SessionDep):
    statement = select(Users).where(Users.id == user_id)
    results = session.exec(statement)
    user = results.one()
    print("User to deactivate: ", user)

    if (user.state == "active"):
        user.state = "deactivated"
        session.add(user)
        session.commit()
        session.refresh(user)
        print("Deactivated User: ", user)
    else: return "Nothing to do, user is not active"

def activate_user_db(user_id: str,session:SessionDep):
    statement = select(Users).where(Users.id == user_id)
    results = session.exec(statement)
    user = results.one()
    print("User to deactivate: ", user)

    if (user.state != "active"):
        user.state = "activated"
        session.add(user)
        session.commit()
        session.refresh(user)
        print("Deactivated User: ", user)
    else: return "Nothing to do, user is active"
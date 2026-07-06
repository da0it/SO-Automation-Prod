from typing import Annotated

import os

from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel

engine = create_engine(os.getenv('SQLALCHEMY_TELEFONY_DATABASE_URL'))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# def change_call_state_db

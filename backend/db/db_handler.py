from dotenv import load_dotenv
from fastapi import Depends

from backend.db.db_models import Users, UserRead, UserCreate, State
import os

from fastapi import Depends
from backend.security.passwords import get_password_hash
from sqlmodel import Session, SQLModel, create_engine, select

from typing import Annotated

load_dotenv()

engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URL'))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

##
## USER RELATED OPERATIONS
##

# ---------------------
# User creation
# ---------------------
def create_user_db(user: UserCreate,session: SessionDep) -> Users:
    try:
        db_user_create = UserCreate.model_validate(user)
        hashed_password = get_password_hash(db_user_create.password)
        db_user = Users(**db_user_create.model_dump(), password_hash=hashed_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except Exception:
        session.rollback()
        raise
# ---------------------



# ---------------------
# Read users from DB
# ---------------------
def read_all_users_db(session: SessionDep):
    statement = select(UserRead)
    results = session.exec(statement).all()
    return results

def read_user_by_email(email: str, session: SessionDep) -> Users | None:
    statement = select(Users).where(Users.email == email)
    user = session.exec(statement).one_or_none()
    if user:
        print("Found user: ", user)
    return user

def read_user_by_id(user_id: int, session: SessionDep) -> Users | None:
    statement = select(Users).where(Users.id == user_id)
    user = session.exec(statement).one_or_none()
    if user:
        print("Found user: ", user)
    return user
# ---------------------



# ---------------------
# User state management
# ---------------------
def activate_user_db(user: Users, session:SessionDep):
    if (user.state == State.ACTIVE):
        return user
    
    user.state = State.ACTIVE
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

def deactivate_user_db(user: Users,session:SessionDep):
    if user.state == State.DEACTIVATED:
        return user

    user.state = State.DEACTIVATED
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

# ---------------------



# ---------------------
# Password hashing and user authentification
# ---------------------

from backend.server import app
from fastapi import APIRouter, HTTPException

from backend.db.db_handler import SessionDep

from db.db_models import Users, UserCreate, UserRead, Role
from db.db_handler import create_user_db, activate_user_db, read_user_db

users_router = APIRouter(
    prefix="/user",
    tags=["User"]
    )

@users_router.post("/register/", response_model=UserRead)
async def create_user_endpoint(user_in: UserCreate, session: SessionDep):
    try:
        new_user = create_user_db(user_in, session)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@users_router.patch("/activate/", response_model=UserRead)
async def activate_user_endpoint(current_user_role: Role, user_id: str, session: SessionDep):
    if (not current_user_role.ADMIN): 
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        activated_user = activate_user_db(user_id, session)
        return activated_user
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@users_router.get("/all_users/")
async def read_users(current_user_role: Role, session: SessionDep):
    if (not current_user_role.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    return read_user_db(session)

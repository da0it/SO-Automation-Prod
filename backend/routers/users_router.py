from fastapi import APIRouter, HTTPException, Depends
from backend.db.db_handler import SessionDep
from backend.db.db_models import Users, UserCreate, UserRead
from backend.db.db_handler import read_all_users_db, deactivate_user_db, activate_user_db, read_user_by_id, read_user_by_email

users_router = APIRouter(
    prefix="/user",
    tags=["User"]
    )

def require_user_by_id(user_id: int, session: SessionDep) -> Users:
    user = read_user_by_id(user_id, session)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def require_user_by_email(email: str, session: SessionDep) -> Users:
    user = read_user_by_email(email, session)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@users_router.patch("/activate/", response_model=UserRead | None)
async def activate_user_endpoint(user_id: int, session: SessionDep):
    try:
        activated_user = activate_user_db(user_id, session)
        return activated_user
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@users_router.patch("/deactivate/", response_model=UserRead | None)
async def deactivate_user_endpoint(user_id: str, session: SessionDep):
    try:
        deactivated_user = deactivate_user_db(user_id, session)
        if deactivated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return deactivated_user
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@users_router.get("/all_users/",response_model=list[UserRead])
async def read_users(session: SessionDep):
    if (not True):
        raise HTTPException(status_code=403, detail="Forbidden")
    return read_all_users_db(session)
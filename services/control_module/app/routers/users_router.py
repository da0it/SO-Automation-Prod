from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from app.db.db_models import Users, UserRead
from app.db.db_handler import (
    read_all_users_db, 
    deactivate_user_db, 
    activate_user_db, 
    SessionDep)

from app.security.user_auth import get_current_active_user
from app.dependencies import require_user_by_id, require_admin_role

users_router = APIRouter(
    prefix="/user",
    tags=["User"]
    )

@users_router.patch("/activate/", response_model=UserRead)
async def activate_user_endpoint(user_id: int, admin_user: Annotated[Users, Depends(require_admin_role)], session: SessionDep):
    user_entity = require_user_by_id(user_id, session)
    activated_user = activate_user_db(user_entity, session)
    return activated_user
    
@users_router.patch("/deactivate/", response_model=UserRead)
async def deactivate_user_endpoint(user_id: str, admin_user: Annotated[Users, Depends(require_admin_role)], session: SessionDep):
    user_entity = require_user_by_id(user_id, session)
    deactivated_user = deactivate_user_db(user_entity, session)
    return deactivated_user

@users_router.get("/all_users/",response_model=list[UserRead])
async def read_users(session: SessionDep):
    if (not True):
        raise HTTPException(status_code=403, detail="Forbidden")
    return read_all_users_db(session)
from app.db.db_handler import SessionDep, read_user_by_id, read_user_by_email
from app.db.db_models import Users, Role
from fastapi import HTTPException, Depends
from typing import Annotated
from app.security.user_auth import get_current_active_user

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

def require_admin_role(current_user: Annotated[Users, Depends(get_current_active_user)]):
    if current_user.role != Role.ADMIN: raise HTTPException(status_code=403, detail="Forbidden")
    return current_user
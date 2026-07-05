from fastapi import HTTPException, Depends, APIRouter, status
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from backend.db.db_handler import SessionDep, create_user_db
from backend.db.db_models import AuthToken, Users, UserRead, UserCreate
from backend.security.auth import authenticate_user, create_access_token, get_current_active_user

import os

auth_router = APIRouter(
    tags=["Authentification"]
)

@auth_router.post("/register/", response_model=UserRead)
async def create_user_endpoint(user_in: UserCreate, session: SessionDep):
    try:
        created_user = create_user_db(user_in, session)
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@auth_router.post("/token",response_model=AuthToken)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> AuthToken:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return AuthToken(access_token=access_token, token_type="bearer")

@auth_router.get("/me/", response_model=UserRead)
async def read_users_me(current_user: Annotated[Users, Depends(get_current_active_user)]) -> UserRead:
    return current_user
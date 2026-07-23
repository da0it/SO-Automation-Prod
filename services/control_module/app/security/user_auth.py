from typing import Annotated
from pwdlib import PasswordHash
from datetime import timezone, timedelta, datetime

import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv

import jwt

from app.db.db_models import Users, State, TokenData
from app.db.db_handler import read_user_by_email, SessionDep



load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hasher = PasswordHash.recommended()

def verify_password(plain_password, password_hash):
    return password_hasher.verify(plain_password, password_hash)

def get_password_hash(password):
    return password_hasher.hash(password)

def authenticate_user(email: str, password: str, session: SessionDep):
    user = read_user_by_email(email, session)

    if user is None:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session:SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = read_user_by_email(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    if current_user.state == State.DEACTIVATED:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
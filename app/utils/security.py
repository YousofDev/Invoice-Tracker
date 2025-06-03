from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.auth.models import User
from app.auth.schemas import TokenData
from app.database import get_db
from app.utils.constants import ALGORITHM, JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_access_token(token_data: TokenData, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    data_to_encode = {"exp": expire, "sub": token_data.model_dump()}
    encoded_jwt = jwt.encode(data_to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    payload = decoded_token.get("sub")
    token_data = TokenData(**payload)

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    return user


def authenticate(request: Request, token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

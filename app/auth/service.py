from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.models import User
from app.auth.schemas import UserCreate, UserInDB, TokenData, Token
from app.utils.security import hash_password, verify_password, create_access_token


class AuthService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def register(self, user_data: UserCreate) -> UserInDB:

        existed_user = self.find_user_by_email(user_data.email)

        if existed_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_dict = user_data.model_dump()

        hashed_password = hash_password(user_dict["password"])

        user_dict["password"] = hashed_password

        user_dict["username"] = user_dict["email"]

        user = User(**user_dict)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserInDB.model_validate(user)

    def login(self, username: str, password: str) -> Token:

        user = self.find_user_by_email(username)

        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token_data = TokenData(user_id=user.id)  # type: ignore

        access_token = create_access_token(token_data)

        return Token(access_token=access_token, token_type="bearer")

    def get_user_list(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_user(self, user_id: int) -> UserInDB:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserInDB.model_validate(user)

    def find_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

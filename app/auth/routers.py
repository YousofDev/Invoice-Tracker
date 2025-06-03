from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.service import AuthService
from app.auth.schemas import UserCreate, UserInDB
from app.utils.security import authenticate, get_current_user

router = APIRouter()


@router.post(
    "/auth/register", status_code=status.HTTP_201_CREATED, response_model=UserInDB
)
def register(user: UserCreate, service: AuthService = Depends()):
    return service.register(user)


@router.post("/auth/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(),
):
    return auth_service.login(form.username, form.password)


@router.get(
    "/auth/profile", dependencies=[Depends(authenticate)], response_model=UserInDB
)
def get_profile(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    return current_user


@router.get("/users", response_model=list[UserInDB])
def get_user_list(skip: int = 0, limit: int = 100, service: AuthService = Depends()):
    return service.get_user_list(skip, limit)


@router.get("/users/{user_id}", response_model=UserInDB)
def get_user(user_id: int, service: AuthService = Depends()):
    return service.get_user(user_id)

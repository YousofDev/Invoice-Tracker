from fastapi import APIRouter, Depends
from app.auth.service import AuthService
from app.auth.schemas import UserCreate, UserInDB, UserUpdate

router = APIRouter()


@router.post("/auth/register", response_model=UserInDB)
def register(user: UserCreate, service: AuthService = Depends()):
    return service.register(user)


@router.get("/users", response_model=list[UserInDB])
def get_user_list(skip: int = 0, limit: int = 100, service: AuthService = Depends()):
    return service.get_user_list(skip, limit)


@router.get("/users/{user_id}", response_model=UserInDB)
def get_user(user_id: int, service: AuthService = Depends()):
    return service.get_user(user_id)

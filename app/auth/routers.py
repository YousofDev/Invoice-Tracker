from fastapi import APIRouter

router = APIRouter()


@router.get("/auth/profile")
def get_user_profile():
    return {"message": "user profile"}

"""User profile endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, UserResponse, UserUpdate
from app.services.user_service import change_password, update_user
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=Envelope[UserResponse])
def get_my_profile(current_user: User = Depends(get_current_user)):
    return ok(current_user)


@router.put("/me", response_model=Envelope[UserResponse])
def update_my_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(update_user(db, current_user, payload))


@router.post("/me/change-password", response_model=Envelope[dict], status_code=status.HTTP_200_OK)
def change_my_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_password(db, current_user, payload)
    return ok({"message": "Password changed successfully."})

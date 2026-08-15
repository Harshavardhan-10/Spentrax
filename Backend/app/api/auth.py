"""Authentication endpoints: register, login, me, logout."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, build_auth_response, register_user
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Envelope[AuthResponse], status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account and return an access token."""
    user = register_user(db, payload)
    return ok(build_auth_response(user))


@router.post("/login", response_model=Envelope[AuthResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return an access token."""
    user = authenticate_user(db, payload.email, payload.password)
    return ok(build_auth_response(user))


@router.get("/me", response_model=Envelope[UserResponse])
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return ok(current_user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Stateless JWT logout: the client discards the token."""
    return ok(None, "Logged out successfully.")

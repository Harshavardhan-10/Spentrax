"""Category endpoints (default + user custom categories)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=Envelope[list[CategoryResponse]])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List default categories plus the current user's custom categories."""
    return ok(list_categories(db, current_user))


@router.post("", response_model=Envelope[CategoryResponse], status_code=status.HTTP_201_CREATED)
def add_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(create_category(db, current_user, payload.name, payload.description))


@router.put("/{category_id}", response_model=Envelope[CategoryResponse])
def edit_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(
        update_category(db, category_id, current_user, payload.name, payload.description)
    )


@router.delete("/{category_id}")
def remove_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_category(db, category_id, current_user)
    return ok(None, "Category deleted successfully.")

"""Category business logic.

Default categories are global (user_id IS NULL) and seeded on startup.
Custom categories are scoped to the creating user and are never visible to
other users. All ownership checks are performed here.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ErrorCode
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User

DEFAULT_CATEGORIES = [
    ("Food", "Meals, groceries and food delivery"),
    ("Transportation", "Fuel, public transport, cabs and ride sharing"),
    ("Shopping", "Clothing, electronics and general shopping"),
    ("Entertainment", "Streaming, movies, games and outings"),
    ("Bills", "Electricity, water, internet and phone bills"),
    ("Healthcare", "Medical consultations, medicines and insurance"),
    ("Education", "Courses, books and tuition"),
    ("Travel", "Flights, hotels and trips"),
    ("Rent", "Rent and housing payments"),
    ("Utilities", "Water, electricity and other utilities"),
    ("Other", "Miscellaneous expenses"),
]


def seed_default_categories(db: Session) -> None:
    for name, description in DEFAULT_CATEGORIES:
        exists = db.scalar(
            select(Category).where(
                Category.name == name, Category.user_id.is_(None)
            )
        )
        if exists is None:
            db.add(
                Category(
                    name=name,
                    description=description,
                    is_default=True,
                    user_id=None,
                )
            )
    db.commit()


def list_categories(db: Session, user: User) -> list[Category]:
    statement = select(Category).where(
        or_(Category.user_id.is_(None), Category.user_id == user.id)
    ).order_by(Category.is_default.desc(), Category.name)
    return list(db.scalars(statement))


def get_category_for_user(db: Session, category_id: int, user: User) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise AppError(
            "Category not found.",
            ErrorCode.CATEGORY_NOT_FOUND,
            status_code=404,
        )
    if category.user_id is not None and category.user_id != user.id:
        raise AppError(
            "You do not have access to this category.",
            ErrorCode.CATEGORY_ACCESS_DENIED,
            status_code=403,
        )
    return category


def create_category(db: Session, user: User, name: str, description: str | None) -> Category:
    name = name.strip()
    if not name:
        raise AppError("Category name is required.", ErrorCode.VALIDATION_ERROR)

    duplicate = db.scalar(
        select(Category).where(
            Category.name == name,
            or_(Category.user_id.is_(None), Category.user_id == user.id),
        )
    )
    if duplicate is not None:
        raise AppError(
            "A category with this name already exists.",
            ErrorCode.CATEGORY_ALREADY_EXISTS,
            status_code=409,
        )

    category = Category(name=name, description=description, is_default=False, user_id=user.id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session, category_id: int, user: User, name: str | None, description: str | None
) -> Category:
    category = get_category_for_user(db, category_id, user)
    if category.user_id != user.id:
        raise AppError(
            "Default categories cannot be modified.",
            ErrorCode.PERMISSION_DENIED,
            status_code=403,
        )

    if name is not None:
        name = name.strip()
        duplicate = db.scalar(
            select(Category).where(
                Category.name == name,
                Category.id != category.id,
                or_(Category.user_id.is_(None), Category.user_id == user.id),
            )
        )
        if duplicate is not None:
            raise AppError(
                "A category with this name already exists.",
                ErrorCode.CATEGORY_ALREADY_EXISTS,
                status_code=409,
            )
        category.name = name
    if description is not None:
        category.description = description.strip() or None

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int, user: User) -> None:
    category = get_category_for_user(db, category_id, user)
    if category.user_id != user.id:
        raise AppError(
            "Default categories cannot be deleted.",
            ErrorCode.PERMISSION_DENIED,
            status_code=403,
        )
    in_use = db.scalar(
        select(Expense.id).where(Expense.category_id == category.id).limit(1)
    )
    if in_use is not None:
        raise AppError(
            "This category is used by existing expenses and cannot be deleted.",
            ErrorCode.PERMISSION_DENIED,
            status_code=409,
        )
    db.delete(category)
    db.commit()

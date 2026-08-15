"""Pytest fixtures for the Smart Expense Manager backend.

The DATABASE_URL must point at a throwaway SQLite file BEFORE the app
modules are imported, because Settings is instantiated at import time.
"""
import os
import tempfile

_temp_db = tempfile.NamedTemporaryFile(prefix="expense_test_", suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_temp_db.name.replace(os.sep, '/')}"
_temp_db.close()

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session", autouse=True)
def create_test_schema():
    """The app relies on Alembic for schema; tests create it directly on the temp DB."""
    from app.core.database import Base, engine
    import app.models.user  # noqa: F401
    import app.models.category  # noqa: F401
    import app.models.expense  # noqa: F401
    import app.models.budget  # noqa: F401
    import app.models.recurring  # noqa: F401
    import app.models.ai_insight  # noqa: F401

    Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Start every test with an empty database (schema kept, data wiped)."""
    from sqlalchemy import text

    from app.core.database import engine

    with engine.begin() as connection:
        for table in (
            "ai_insights",
            "recurring_expenses",
            "expenses",
            "budgets",
            "categories",
            "users",
        ):
            connection.execute(text(f"DELETE FROM {table}"))


@pytest.fixture
def client():
    """A TestClient with lifespan running (default categories get seeded)."""
    with TestClient(app) as test_client:
        yield test_client


def register_user(client, name, email, password="password123"):
    response = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    return data["user"], {"Authorization": f"Bearer {data['access_token']}"}


@pytest.fixture
def users(client):
    """Two isolated users (user_a owns data, user_b is the intruder)."""
    user_a, headers_a = register_user(client, "User A", "user_a@example.com")
    user_b, headers_b = register_user(client, "User B", "user_b@example.com")
    return {
        "a": user_a,
        "b": user_b,
        "headers_a": headers_a,
        "headers_b": headers_b,
    }


@pytest.fixture
def auth_headers(client):
    _, headers = register_user(client, "Tester", "tester@example.com")
    return headers


@pytest.fixture
def categories(client, auth_headers):
    """All categories visible to the authenticated user (defaults + customs)."""
    response = client.get("/categories", headers=auth_headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def category_id(categories, name):
    for category in categories:
        if category["name"] == name:
            return category["id"]
    raise AssertionError(f"Category {name!r} not found in {categories}")
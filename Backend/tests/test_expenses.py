"""Expense tests: CRUD, filters, pagination, validation, isolation."""
from conftest import category_id


def _create_expense(client, headers, categories, **overrides):
    payload = {
        "description": "Dinner at restaurant",
        "merchant": "Swiggy",
        "amount": 250.0,
        "category_id": category_id(categories, "Food"),
        "payment_method": "UPI",
        "expense_date": "2026-08-05",
    }
    payload.update(overrides)
    response = client.post("/expenses", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_create_expense(client, auth_headers, categories):
    data = _create_expense(client, auth_headers, categories)
    assert data["description"] == "Dinner at restaurant"
    assert data["category_name"] == "Food"
    assert data["amount"] == 250.0
    assert data["user_id"] is not None


def test_create_expense_invalid_amount(client, auth_headers, categories):
    response = client.post(
        "/expenses",
        headers=auth_headers,
        json={
            "description": "Bogus",
            "amount": -10,
            "category_id": category_id(categories, "Food"),
            "expense_date": "2026-08-05",
        },
    )
    assert response.status_code == 422


def test_create_expense_invalid_category(client, auth_headers, categories):
    response = client.post(
        "/expenses",
        headers=auth_headers,
        json={
            "description": "Bogus",
            "amount": 10,
            "category_id": 999999,
            "expense_date": "2026-08-05",
        },
    )
    assert response.status_code == 404


def test_create_expense_others_category(client, users):
    private = client.post(
        "/categories", headers=users["headers_a"], json={"name": "Private"}
    ).json()["data"]
    response = client.post(
        "/expenses",
        headers=users["headers_b"],
        json={
            "description": "Sneaky",
            "amount": 10,
            "category_id": private["id"],
            "expense_date": "2026-08-05",
        },
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "CATEGORY_ACCESS_DENIED"


def test_list_expenses_paginated(client, auth_headers, categories):
    for i in range(5):
        _create_expense(client, auth_headers, categories, description=f"Item {i}")
    response = client.get(
        "/expenses", headers=auth_headers, params={"limit": 2, "page": 1}
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert len(body["items"]) == 2
    assert body["total"] == 5
    assert body["pages"] == 3


def test_filter_by_category(client, auth_headers, categories):
    transport_id = category_id(categories, "Transportation")
    for _ in range(3):
        _create_expense(client, auth_headers, categories, description="Food run")
    _create_expense(
        client,
        auth_headers,
        categories,
        description="Cab ride",
        category_id=transport_id,
    )
    response = client.get(
        "/expenses", headers=auth_headers, params={"category": transport_id}
    )
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["category_name"] == "Transportation"


def test_search_description(client, auth_headers, categories):
    _create_expense(client, auth_headers, categories, description="Coffee beans")
    _create_expense(client, auth_headers, categories, description="Gym membership")
    response = client.get(
        "/expenses", headers=auth_headers, params={"search": "coffee"}
    )
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["description"] == "Coffee beans"


def test_filter_amount_range(client, auth_headers, categories):
    _create_expense(client, auth_headers, categories, description="Small", amount=50)
    _create_expense(client, auth_headers, categories, description="Medium", amount=200)
    _create_expense(client, auth_headers, categories, description="Big", amount=2000)
    response = client.get(
        "/expenses",
        headers=auth_headers,
        params={"min_amount": 100, "max_amount": 500},
    )
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["description"] == "Medium"


def test_filter_date_range(client, auth_headers, categories):
    _create_expense(client, auth_headers, categories, description="Early", expense_date="2026-08-01")
    _create_expense(client, auth_headers, categories, description="Late", expense_date="2026-08-31")
    response = client.get(
        "/expenses",
        headers=auth_headers,
        params={"start_date": "2026-08-10", "end_date": "2026-08-20"},
    )
    assert response.json()["data"]["total"] == 0


def test_get_single_expense(client, auth_headers, categories):
    created = _create_expense(client, auth_headers, categories)
    response = client.get(f"/expenses/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created["id"]


def test_update_expense(client, auth_headers, categories):
    created = _create_expense(client, auth_headers, categories)
    response = client.put(
        f"/expenses/{created['id']}",
        headers=auth_headers,
        json={"amount": 999.5, "description": "Updated meal"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["amount"] == 999.5
    assert data["description"] == "Updated meal"


def test_delete_expense(client, auth_headers, categories):
    created = _create_expense(client, auth_headers, categories)
    response = client.delete(f"/expenses/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    details = client.get(f"/expenses/{created['id']}", headers=auth_headers)
    assert details.status_code == 404


def test_cross_user_access_forbidden(client, users, categories):
    created = _create_expense(client, users["headers_a"], categories, description="Secret")
    response = client.get(f"/expenses/{created['id']}", headers=users["headers_b"])
    assert response.status_code == 404

    update = client.put(
        f"/expenses/{created['id']}",
        headers=users["headers_b"],
        json={"amount": 1},
    )
    assert update.status_code == 404

    delete = client.delete(f"/expenses/{created['id']}", headers=users["headers_b"])
    assert delete.status_code == 404
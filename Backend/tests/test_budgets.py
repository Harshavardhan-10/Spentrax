"""Budget tests: CRUD, duplication, usage reporting, isolation."""
from conftest import category_id

MONTH = 8
YEAR = 2026


def _create_budget(client, headers, categories, **overrides):
    payload = {
        "category_id": category_id(categories, "Food"),
        "amount": 5000.0,
        "month": MONTH,
        "year": YEAR,
    }
    payload.update(overrides)
    response = client.post("/budgets", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_create_budget(client, auth_headers, categories):
    data = _create_budget(client, auth_headers, categories)
    assert data["category_name"] == "Food"
    assert data["amount"] == 5000.0


def test_duplicate_budget_rejected(client, auth_headers, categories):
    _create_budget(client, auth_headers, categories)
    response = client.post(
        "/budgets",
        headers=auth_headers,
        json={"category_id": category_id(categories, "Food"), "amount": 100, "month": MONTH, "year": YEAR},
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "BUDGET_ALREADY_EXISTS"


def test_same_category_other_month_allowed(client, auth_headers, categories):
    _create_budget(client, auth_headers, categories)
    data = _create_budget(client, auth_headers, categories, month=9)
    assert data["month"] == 9


def test_budget_usage_reported(client, auth_headers, categories):
    food_id = category_id(categories, "Food")
    _create_budget(client, auth_headers, categories, amount=1000)
    client.post(
        "/expenses",
        headers=auth_headers,
        json={
            "description": "Lunch",
            "amount": 250,
            "category_id": food_id,
            "expense_date": f"{YEAR}-{MONTH:02d}-05",
        },
    )
    response = client.get(
        "/budgets", headers=auth_headers, params={"month": MONTH, "year": YEAR}
    )
    assert response.status_code == 200
    items = response.json()["data"]
    assert len(items) == 1
    usage = items[0]
    assert usage["spent"] == 250.0
    assert usage["remaining"] == 750.0
    assert usage["used_percentage"] == 25.0
    assert usage["status"] == "HEALTHY"


def test_budget_statuses(client, auth_headers, categories):
    food_id = category_id(categories, "Food")
    entertainment_id = category_id(categories, "Entertainment")
    bills_id = category_id(categories, "Bills")

    def make_budget(category_id, amount, expense_amount):
        client.post(
            "/budgets",
            headers=auth_headers,
            json={"category_id": category_id, "amount": amount, "month": MONTH, "year": YEAR},
        )
        client.post(
            "/expenses",
            headers=auth_headers,
            json={
                "description": f"Spend {expense_amount}",
                "amount": expense_amount,
                "category_id": category_id,
                "expense_date": f"{YEAR}-{MONTH:02d}-05",
            },
        )

    make_budget(food_id, 1000, 250)
    make_budget(entertainment_id, 300, 220)
    make_budget(bills_id, 1000, 1500)

    response = client.get(
        "/budgets", headers=auth_headers, params={"month": MONTH, "year": YEAR}
    )
    data = response.json()["data"]

    small = [i for i in data if i["category_name"] == "Food"][0]
    near = [i for i in data if i["category_name"] == "Entertainment"][0]
    over = [i for i in data if i["category_name"] == "Bills"][0]
    assert small["status"] == "HEALTHY"
    assert near["status"] == "WARNING"
    assert over["status"] == "EXCEEDED"


def test_update_budget(client, auth_headers, categories):
    created = _create_budget(client, auth_headers, categories)
    response = client.put(
        f"/budgets/{created['id']}", headers=auth_headers, json={"amount": 8000}
    )
    assert response.status_code == 200
    assert response.json()["data"]["amount"] == 8000.0


def test_delete_budget(client, auth_headers, categories):
    created = _create_budget(client, auth_headers, categories)
    response = client.delete(f"/budgets/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    listing = client.get("/budgets", headers=auth_headers, params={"month": MONTH, "year": YEAR}).json()["data"]
    assert created["id"] not in {i["id"] for i in listing}


def test_cross_user_budget_isolated(client, users, categories):
    created = _create_budget(client, users["headers_a"], categories)
    response = client.get(f"/budgets", headers=users["headers_b"], params={"month": MONTH, "year": YEAR})
    assert created["id"] not in {i["id"] for i in response.json()["data"]}

    update = client.put(
        f"/budgets/{created['id']}", headers=users["headers_b"], json={"amount": 1}
    )
    assert update.status_code == 404

    delete = client.delete(f"/budgets/{created['id']}", headers=users["headers_b"])
    assert delete.status_code == 404
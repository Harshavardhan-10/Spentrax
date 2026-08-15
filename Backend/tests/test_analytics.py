"""Analytics endpoint tests."""
from conftest import category_id


def _add_expense(client, headers, categories, description, amount, date, merchant=None):
    response = client.post(
        "/expenses",
        headers=headers,
        json={
            "description": description,
            "merchant": merchant,
            "amount": amount,
            "category_id": category_id(categories, "Food"),
            "expense_date": date,
        },
    )
    assert response.status_code == 201, response.text


def test_monthly_analytics_totals(client, auth_headers, categories):
    _add_expense(client, auth_headers, categories, "Lunch", 100, "2026-08-02")
    _add_expense(client, auth_headers, categories, "Dinner", 200, "2026-08-15")
    response = client.get(
        "/analytics/monthly", headers=auth_headers, params={"month": 8, "year": 2026}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["month"] == 8
    assert data["year"] == 2026
    assert data["total_expenses"] == 300.0
    assert data["highest_expense"]["amount"] == 200.0
    assert data["lowest_expense"]["amount"] == 100.0
    assert data["top_category"]["category_name"] == "Food"


def test_category_breakdown_percentages(client, auth_headers, categories):
    transport_id = category_id(categories, "Transportation")
    _add_expense(client, auth_headers, categories, "Lunch", 300, "2026-08-02")
    client.post(
        "/expenses",
        headers=auth_headers,
        json={
            "description": "Cab",
            "amount": 100,
            "category_id": transport_id,
            "expense_date": "2026-08-03",
        },
    )
    response = client.get(
        "/analytics/categories", headers=auth_headers, params={"month": 8, "year": 2026}
    )
    data = response.json()["data"]
    by_name = {item["category_name"]: item for item in data}
    assert by_name["Food"]["amount"] == 300.0
    assert by_name["Food"]["percentage"] == 75.0
    assert by_name["Transportation"]["amount"] == 100.0
    assert by_name["Transportation"]["percentage"] == 25.0


def test_trends_returns_months(client, auth_headers, categories):
    _add_expense(client, auth_headers, categories, "Lunch", 100, "2026-08-02")
    response = client.get("/analytics/trends", headers=auth_headers, params={"months": 6})
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 6
    august = [p for p in data if p["year"] == 2026 and p["month"] == 8]
    assert august and august[0]["total"] == 100.0


def test_comparison_with_previous_month(client, auth_headers, categories):
    _add_expense(client, auth_headers, categories, "Lunch", 100, "2026-07-10")
    _add_expense(client, auth_headers, categories, "Lunch", 300, "2026-08-10")
    response = client.get(
        "/analytics/comparison", headers=auth_headers, params={"month": 8, "year": 2026}
    )
    data = response.json()["data"]
    assert data["current_total"] == 300.0
    assert data["previous_total"] == 100.0
    assert data["difference"] == 200.0


def test_analytics_respects_user_isolation(client, users, categories):
    _add_expense(client, users["headers_a"], categories, "Lunch", 500, "2026-08-10")
    response = client.get(
        "/analytics/monthly", headers=users["headers_b"], params={"month": 8, "year": 2026}
    )
    assert response.json()["data"]["total_expenses"] == 0.0
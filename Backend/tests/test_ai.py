"""AI endpoint tests: categorization, insights, summary, recommendations."""
from conftest import category_id


def _add_expense(client, headers, categories, description, amount, date, category=None):
    response = client.post(
        "/expenses",
        headers=headers,
        json={
            "description": description,
            "amount": amount,
            "category_id": category_id(categories, category or "Food"),
            "expense_date": date,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_categorize_food_keywords(client, auth_headers):
    response = client.post(
        "/ai/categorize",
        headers=auth_headers,
        json={"description": "Swiggy dinner with friends", "merchant": "Swiggy"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["category"] == "Food"
    assert data["confidence"] > 0.5
    assert data["reason"]


def test_categorize_transport_keywords(client, auth_headers):
    response = client.post(
        "/ai/categorize",
        headers=auth_headers,
        json={"description": "Uber ride to office"},
    )
    assert response.json()["data"]["category"] == "Transportation"


def test_categorize_unknown_text(client, auth_headers):
    response = client.post(
        "/ai/categorize",
        headers=auth_headers,
        json={"description": "qwxzz nonsense 12345"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["category"] in ("Other", "Uncategorized")
    assert data["confidence"] <= 0.5


def test_categorize_requires_auth(client):
    response = client.post(
        "/ai/categorize", json={"description": "Coffee"}
    )
    assert response.status_code == 401


def test_recommendations_include_category_id(client, auth_headers, categories):
    for month_day in [("2026-06-05", 500), ("2026-07-05", 600), ("2026-08-05", 700)]:
        _add_expense(client, auth_headers, categories, "Groceries run", month_day[1], month_day[0])
    response = client.get("/ai/recommendations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    food_rec = [r for r in data if r["category"] == "Food"]
    assert food_rec
    assert food_rec[0]["category_id"] == category_id(categories, "Food")
    assert food_rec[0]["recommended_budget"] > 0
    assert food_rec[0]["reason"]


def test_summary_generated(client, auth_headers, categories):
    _add_expense(client, auth_headers, categories, "Lunch", 250, "2026-08-05")
    response = client.get("/ai/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["summary"]
    assert data["month"] == 8
    assert data["year"] == 2026


def test_insights_refresh_persists(client, auth_headers, categories):
    _add_expense(client, auth_headers, categories, "Lunch", 250, "2026-08-05")
    _add_expense(client, auth_headers, categories, "Dinner", 450, "2026-08-06")
    response = client.get("/ai/insights", headers=auth_headers, params={"refresh": True})
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    assert data[0]["title"]
    assert data[0]["content"]

    cached = client.get("/ai/insights", headers=auth_headers)
    assert cached.status_code == 200
    assert len(cached.json()["data"]) == len(data)


def test_anomalies_endpoint(client, auth_headers, categories):
    response = client.get("/ai/anomalies", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_ai_respects_user_isolation(client, users, categories):
    _add_expense(client, users["headers_a"], categories, "Lunch", 250, "2026-08-05")
    response = client.get("/ai/summary", headers=users["headers_b"])
    assert response.status_code == 200
    assert "Lunch" not in response.json()["data"]["summary"]
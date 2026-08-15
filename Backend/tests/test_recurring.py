"""Recurring expense detection and management tests."""
from conftest import category_id


def _add_expense(client, headers, categories, merchant, amount, date):
    response = client.post(
        "/expenses",
        headers=headers,
        json={
            "description": merchant,
            "merchant": merchant,
            "amount": amount,
            "category_id": category_id(categories, "Bills"),
            "expense_date": date,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_detects_weekly_pattern(client, auth_headers, categories):
    for week_offset, amount in enumerate([649, 649, 649]):
        _add_expense(
            client, auth_headers, categories, "Netflix", amount,
            f"2026-07-{1 + week_offset * 7:02d}",
        )
    response = client.post("/recurring/detect", headers=auth_headers)
    assert response.status_code == 200
    detected = response.json()["data"]
    netflix = [i for i in detected if i["name"] == "Netflix"]
    assert len(netflix) == 1
    item = netflix[0]
    assert item["frequency"] in ("WEEKLY", "MONTHLY")
    assert item["confidence_score"] >= 0.8
    assert item["amount"] == 649.0
    assert item["is_active"] is True


def test_detection_ignores_irregular_expenses(client, auth_headers, categories):
    for amount, day in [(100, 1), (999, 10), (50, 22)]:
        _add_expense(client, auth_headers, categories, "RandomShop", amount, f"2026-07-{day:02d}")
    response = client.post("/recurring/detect", headers=auth_headers)
    assert response.status_code == 200
    detected = response.json()["data"]
    assert "RandomShop" not in {i["name"] for i in detected}


def test_detection_requires_three_occurrences(client, auth_headers, categories):
    _add_expense(client, auth_headers, categories, "Gym", 500, "2026-07-01")
    _add_expense(client, auth_headers, categories, "Gym", 500, "2026-07-08")
    response = client.post("/recurring/detect", headers=auth_headers)
    detected = response.json()["data"]
    assert "Gym" not in {i["name"] for i in detected}


def test_toggle_active(client, auth_headers, categories):
    for week_offset in range(3):
        _add_expense(client, auth_headers, categories, "Prime", 149, f"2026-07-{1 + week_offset * 7:02d}")
    created = client.post("/recurring/detect", headers=auth_headers).json()["data"][0]

    response = client.patch(
        f"/recurring/{created['id']}",
        headers=auth_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False

    listing = client.get("/recurring", headers=auth_headers).json()["data"]
    matching = [i for i in listing if i["id"] == created["id"]]
    assert matching and matching[0]["is_active"] is False


def test_delete_recurring(client, auth_headers, categories):
    for week_offset in range(3):
        _add_expense(client, auth_headers, categories, "Spotify", 119, f"2026-07-{1 + week_offset * 7:02d}")
    created = client.post("/recurring/detect", headers=auth_headers).json()["data"][0]
    response = client.delete(f"/recurring/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    listing = client.get("/recurring", headers=auth_headers).json()["data"]
    assert created["id"] not in {i["id"] for i in listing}


def test_cross_user_recurring_isolated(client, users, categories):
    for week_offset in range(3):
        _add_expense(client, users["headers_a"], categories, "Hulu", 500, f"2026-07-{1 + week_offset * 7:02d}")
    created = client.post("/recurring/detect", headers=users["headers_a"]).json()["data"][0]

    visible = client.get("/recurring", headers=users["headers_b"]).json()["data"]
    assert created["id"] not in {i["id"] for i in visible}

    response = client.patch(
        f"/recurring/{created['id']}", headers=users["headers_b"], json={"is_active": False}
    )
    assert response.status_code == 404
    response = client.delete(f"/recurring/{created['id']}", headers=users["headers_b"])
    assert response.status_code == 404
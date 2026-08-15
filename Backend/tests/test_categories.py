"""Category tests: defaults, custom CRUD, access rules."""
from conftest import category_id


def test_list_includes_default_categories(client, auth_headers):
    response = client.get("/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    names = {c["name"] for c in data}
    assert {"Food", "Transportation", "Entertainment", "Bills"} <= names
    assert all(c["is_default"] for c in data if c["name"] == "Food")


def test_create_custom_category(client, auth_headers):
    response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "Groceries", "description": "Weekly groceries"},
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Groceries"
    assert data["is_default"] is False


def test_create_duplicate_category(client, auth_headers, categories):
    duplicate_name = next(c["name"] for c in categories)
    response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": duplicate_name},
    )
    assert response.status_code == 409


def test_create_duplicate_custom_category(client, auth_headers):
    client.post("/categories", headers=auth_headers, json={"name": "Pets"})
    response = client.post("/categories", headers=auth_headers, json={"name": "Pets"})
    assert response.status_code == 409


def test_update_custom_category(client, auth_headers):
    created = client.post(
        "/categories", headers=auth_headers, json={"name": "Pets"}
    ).json()["data"]
    response = client.put(
        f"/categories/{created['id']}",
        headers=auth_headers,
        json={"name": "Pet Care", "description": "Vet and food"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Pet Care"
    assert data["description"] == "Vet and food"


def test_default_category_cannot_be_modified(client, auth_headers, categories):
    default_id = category_id(categories, "Food")
    response = client.put(
        f"/categories/{default_id}", headers=auth_headers, json={"name": "Foodies"}
    )
    assert response.status_code == 403
    assert response.json()["success"] is False


def test_default_category_cannot_be_deleted(client, auth_headers, categories):
    default_id = category_id(categories, "Food")
    response = client.delete(f"/categories/{default_id}", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["success"] is False


def test_delete_custom_category(client, auth_headers):
    created = client.post(
        "/categories", headers=auth_headers, json={"name": "Pets"}
    ).json()["data"]
    response = client.delete(f"/categories/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    remaining = client.get("/categories", headers=auth_headers).json()["data"]
    assert created["id"] not in {c["id"] for c in remaining}


def test_user_cannot_see_others_custom_categories(client, users, auth_headers):
    created = client.post(
        "/categories", headers=auth_headers, json={"name": "Private"}
    ).json()["data"]
    visible = client.get("/categories", headers=users["headers_b"]).json()["data"]
    assert created["id"] not in {c["id"] for c in visible}


def test_user_cannot_modify_others_category(client, users, auth_headers):
    created = client.post(
        "/categories", headers=auth_headers, json={"name": "Private"}
    ).json()["data"]
    response = client.put(
        f"/categories/{created['id']}",
        headers=users["headers_b"],
        json={"name": "Hacked"},
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "CATEGORY_ACCESS_DENIED"
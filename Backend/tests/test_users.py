"""User profile tests: update profile and change password."""


def _register(client, email, password="password123"):
    response = client.post(
        "/auth/register",
        json={"name": "User", "email": email, "password": password},
    )
    data = response.json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}


def test_update_profile_name(client):
    headers = _register(client, "userprofile@example.com")
    response = client.put(
        "/users/me",
        headers=headers,
        json={"name": "Renamed"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Renamed"
    assert response.json()["data"]["email"] == "userprofile@example.com"


def test_update_profile_email(client):
    headers = _register(client, "userprofile2@example.com")
    response = client.put(
        "/users/me",
        headers=headers,
        json={"email": "renamed@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "renamed@example.com"


def test_update_profile_email_taken(client):
    headers_a = _register(client, "taken_a@example.com")
    _register(client, "taken_b@example.com")
    response = client.put(
        "/users/me",
        headers=headers_a,
        json={"email": "taken_b@example.com"},
    )
    assert response.status_code == 409
    assert response.json()["success"] is False


def test_update_profile_requires_auth(client):
    headers = _register(client, "userprofile3@example.com")
    response = client.put("/users/me", json={"name": "Nope"})
    assert response.status_code == 401


def test_change_password_wrong_current(client):
    headers = _register(client, "changepass@example.com")
    response = client.post(
        "/users/me/change-password",
        headers=headers,
        json={"current_password": "wrong", "new_password": "newpassword456"},
    )
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_change_password_same_as_current(client):
    headers = _register(client, "changepass2@example.com")
    response = client.post(
        "/users/me/change-password",
        headers=headers,
        json={"current_password": "password123", "new_password": "password123"},
    )
    assert response.status_code == 400


def test_change_password_short_new(client):
    headers = _register(client, "changepass3@example.com")
    response = client.post(
        "/users/me/change-password",
        headers=headers,
        json={"current_password": "password123", "new_password": "short"},
    )
    assert response.status_code == 422


def test_change_password_success_and_login(client):
    headers = _register(client, "changepass4@example.com")
    response = client.post(
        "/users/me/change-password",
        headers=headers,
        json={"current_password": "password123", "new_password": "brandnew789"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    old_login = client.post(
        "/auth/login",
        json={"email": "changepass4@example.com", "password": "password123"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": "changepass4@example.com", "password": "brandnew789"},
    )
    assert new_login.status_code == 200
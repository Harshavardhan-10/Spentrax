"""Authentication endpoint tests: register, login, me, logout."""


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"name": "New User", "email": "fresh@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["user"]["email"] == "fresh@example.com"


def test_register_duplicate_email(client):
    payload = {"name": "Dup", "email": "dup@example.com", "password": "password123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={"name": "Short", "email": "short@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"name": "Login User", "email": "login@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"name": "Login User", "email": "login@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_me_with_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert response.status_code in (401, 403)


def test_me_returns_profile(client):
    client.post(
        "/auth/register",
        json={"name": "Profile", "email": "profile@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "profile@example.com", "password": "password123"},
    ).json()["data"]
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Profile"
    assert data["email"] == "profile@example.com"
    assert "password_hash" not in data


def test_logout(client, auth_headers):
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_expired_token_rejected(client):
    import jwt

    from app.core.config import get_settings

    settings = get_settings()
    expired = jwt.encode(
        {"sub": "999", "exp": 0},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code in (401, 403)
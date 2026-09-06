from starlette import status

REGISTER_PAYLOAD = {
    "email": "user@example.com",
    "username": "johndoe",
    "password": "supersecret123",
}


def _register(client, **overrides):
    payload = {**REGISTER_PAYLOAD, **overrides}
    return client.post("/auth/register", json=payload)


def _login(client, email=REGISTER_PAYLOAD["email"], password=REGISTER_PAYLOAD["password"]):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register(client):
    response = _register(client)
    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert body["email"] == REGISTER_PAYLOAD["email"]
    assert body["username"] == REGISTER_PAYLOAD["username"]
    assert body["is_active"] is True
    assert "hashed_password" not in body
    assert "id" in body


def test_register_duplicate_email(client):
    _register(client)
    response = _register(client, username="other")
    assert response.status_code == status.HTTP_409_CONFLICT


def test_register_duplicate_username(client):
    _register(client)
    response = _register(client, email="other@example.com")
    assert response.status_code == status.HTTP_409_CONFLICT


def test_login_success_and_me(client):
    _register(client)

    login = _login(client)
    assert login.status_code == status.HTTP_200_OK
    token = login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["email"] == REGISTER_PAYLOAD["email"]


def test_login_wrong_password(client):
    _register(client)
    response = _login(client, password="wrong-password")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_with_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_and_delete_me(client):
    _register(client)
    token = _login(client).json()["access_token"]

    update = client.patch(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "newusername"},
    )
    assert update.status_code == status.HTTP_200_OK
    assert update.json()["username"] == "newusername"

    delete = client.delete("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == status.HTTP_204_NO_CONTENT

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == status.HTTP_404_NOT_FOUND

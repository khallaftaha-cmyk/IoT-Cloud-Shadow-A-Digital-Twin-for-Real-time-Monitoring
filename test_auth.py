import pytest

TEST_EMAIL = "testuser@twin.local"
TEST_PASSWORD = "testpassword123"


def test_register_user(client):
    response = client.post("/users/", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_EMAIL
    assert "id" in data


def test_register_duplicate_user(client):
    client.post("/users/", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    response = client.post("/users/", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 409


def test_login_success(client):
    client.post("/users/", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    response = client.post("/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/users/", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    response = client.post("/login", data={
        "username": TEST_EMAIL,
        "password": "wrongpassword"
    })
    assert response.status_code == 403


def test_protected_route_without_token(client):
    response = client.get("/twin-status")
    assert response.status_code == 401
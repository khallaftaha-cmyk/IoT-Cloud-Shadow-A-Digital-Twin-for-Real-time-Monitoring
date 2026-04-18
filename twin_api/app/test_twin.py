import pytest
from datetime import datetime

TEST_EMAIL = "sensortest@twin.local"
TEST_PASSWORD = "sensorpassword123"


@pytest.fixture()
def auth_headers(client):
    client.post("/users/", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    response = client.post("/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_twin_status_authenticated(client, auth_headers):
    response = client.get("/twin-status", headers=auth_headers)
    assert response.status_code == 200
    assert "sensor_01" in response.json()


def test_update_twin(client, auth_headers):
    payload = {
        "device_id": "sensor_01",
        "temperature": 23.5,
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }
    response = client.post("/update-twin", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["temperature"] == 23.5
    assert data["device_id"] == "sensor_01"


def test_get_history(client, auth_headers):
    response = client.get("/history?limit=5", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_twin_without_token(client):
    payload = {
        "device_id": "sensor_01",
        "temperature": 22.0,
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }
    response = client.post("/update-twin", json=payload)
    assert response.status_code == 401
import pytest

TEST_EMAIL = "actuatortest@twin.local"
TEST_PASSWORD = "password123"


@pytest.fixture()
def auth_headers(client):
    client.post("/users/", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    response = client.post("/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_issue_actuation_command(client, auth_headers):
    payload = {
        "device_id": "sensor_01",
        "command": "COOLING_ON",
        "params": {"speed": 100}
    }
    response = client.post("/actuate/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["command"] == "COOLING_ON"
    assert data["status"] == "pending"
    assert "id" in data


def test_get_pending_commands(client, auth_headers):
    client.post("/actuate/", json={"device_id": "sensor_01", "command": "HEATING_OFF"}, headers=auth_headers)
    response = client.get("/actuate/pending/sensor_01")
    assert response.status_code == 200
    commands = response.json()
    assert isinstance(commands, list)
    assert len(commands) > 0


def test_actuation_history(client, auth_headers):
    response = client.get("/actuate/history?device_id=sensor_01", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_command_status(client, auth_headers):
    res = client.post("/actuate/", json={"device_id": "sensor_01", "command": "TEST_CMD"}, headers=auth_headers)
    cmd_id = res.json()["id"]

    patch_res = client.patch(f"/actuate/{cmd_id}/status", json={"status": "executed"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "executed"

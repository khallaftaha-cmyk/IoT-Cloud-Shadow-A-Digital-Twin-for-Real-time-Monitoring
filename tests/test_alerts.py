import pytest

TEST_EMAIL = "alerttest@twin.local"
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


def test_create_alert_rule(client, auth_headers):
    rule_payload = {
        "device_id": "sensor_01",
        "metric": "temperature",
        "operator": ">",
        "threshold": 30.0,
        "severity": "critical"
    }
    response = client.post("/alerts/rules", json=rule_payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["metric"] == "temperature"
    assert data["threshold"] == 30.0


def test_list_alert_rules(client, auth_headers):
    response = client.get("/alerts/rules", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_alert_triggered_on_threshold_breach(client, auth_headers):
    # 1. Create rule: temperature > 25.0
    client.post("/alerts/rules", json={
        "device_id": "sensor_01",
        "metric": "temperature",
        "operator": ">",
        "threshold": 25.0,
        "severity": "warning"
    }, headers=auth_headers)

    # 2. Send telemetry breaching threshold (35.0°C)
    telemetry = {
        "device_id": "sensor_01",
        "temperature": 35.0,
        "status": "online",
        "timestamp": "2026-08-12T12:00:00"
    }
    client.post("/update-twin", json=telemetry, headers=auth_headers)

    # 3. Verify alert was generated
    alert_res = client.get("/alerts?device_id=sensor_01", headers=auth_headers)
    assert alert_res.status_code == 200
    alerts = alert_res.json()
    assert len(alerts) > 0
    assert alerts[0]["value"] == 35.0


def test_acknowledge_alert(client, auth_headers):
    alert_res = client.get("/alerts?device_id=sensor_01", headers=auth_headers)
    alerts = alert_res.json()
    if alerts:
        alert_id = alerts[0]["id"]
        ack_res = client.patch(f"/alerts/{alert_id}/acknowledge", headers=auth_headers)
        assert ack_res.status_code == 200
        assert ack_res.json()["acknowledged"] is True

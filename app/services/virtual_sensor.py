import requests
import requests
import time
import random
import os

BASE_URL = "http://localhost:8000"
DEVICE_ID = "sensor_01"

SENSOR_EMAIL = os.getenv("SENSOR_EMAIL", "sensor@twin.local")
SENSOR_PASSWORD = os.getenv("SENSOR_PASSWORD", "sensor_password")


def get_token() -> str:
    response = requests.post(
        f"{BASE_URL}/login",
        data={"username": SENSOR_EMAIL, "password": SENSOR_PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"[AUTH] Token acquired for '{SENSOR_EMAIL}'")
        return token
    raise RuntimeError(f"Login failed: {response.status_code} {response.text}")


def generate_temperature(current_temp: float) -> float:
    return round(current_temp + random.uniform(-0.5, 0.5), 2)


def run_virtual_sensor():
    current_temp = 22.0
    print("Starting Virtual Sensor")

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    try:
        while True:
            current_temp = generate_temperature(current_temp)

            payload = {
                "device_id": DEVICE_ID,
                "temperature": current_temp,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "online"
            }

            try:
                response = requests.post(
                    f"{BASE_URL}/update-twin",
                    json=payload,
                    headers=headers
                )
                if response.status_code == 401:
                    print("[AUTH] Token expired, refreshing...")
                    token = get_token()
                    headers = {"Authorization": f"Bearer {token}"}
                else:
                    print(f"Sent: {current_temp}°C | Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("Error: Backend is offline. Retrying...")

            time.sleep(2)
    except KeyboardInterrupt:
        print("Sensor stopped by user")


if __name__ == "__main__":
    run_virtual_sensor()
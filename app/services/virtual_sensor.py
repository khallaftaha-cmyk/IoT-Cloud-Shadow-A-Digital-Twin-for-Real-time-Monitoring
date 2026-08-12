import requests
import time
import random
import os

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
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


def generate_telemetry(current_temp: float, current_hum: float, current_press: float, battery: float):
    new_temp = round(current_temp + random.uniform(-0.5, 0.5), 2)
    new_hum = round(max(10.0, min(99.0, current_hum + random.uniform(-1.0, 1.0))), 2)
    new_press = round(current_press + random.uniform(-0.2, 0.2), 2)
    new_battery = round(max(0.0, battery - 0.01), 2)
    return new_temp, new_hum, new_press, new_battery


def run_virtual_sensor():
    current_temp = 22.0
    current_hum = 45.0
    current_press = 1013.25
    battery = 100.0

    print("=" * 50)
    print("  Virtual IoT Sensor Simulator — Multi-Telemetry")
    print("=" * 50)

    try:
        token = get_token()
    except Exception as e:
        print(f"[WARNING] Could not authenticate directly ({e}). Proceeding unauthenticated if backend allows...")
        token = ""

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        while True:
            current_temp, current_hum, current_press, battery = generate_telemetry(
                current_temp, current_hum, current_press, battery
            )

            payload = {
                "device_id": DEVICE_ID,
                "temperature": current_temp,
                "humidity": current_hum,
                "pressure": current_press,
                "battery_level": battery,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "online",
                "extra_metadata": {"firmware": "v2.1.0", "location": "Building A, Floor 2"}
            }

            try:
                response = requests.post(
                    f"{BASE_URL}/update-twin",
                    json=payload,
                    headers=headers
                )
                if response.status_code == 401:
                    print("[AUTH] Token expired, refreshing...")
                    try:
                        token = get_token()
                        headers = {"Authorization": f"Bearer {token}"}
                    except Exception:
                        pass
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Telemetry Sent: {current_temp}°C | {current_hum}% RH | {current_press} hPa | Batt: {battery}% | Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("Error: Backend is offline. Retrying...")

            time.sleep(2)
    except KeyboardInterrupt:
        print("Sensor stopped by user")


if __name__ == "__main__":
    run_virtual_sensor()
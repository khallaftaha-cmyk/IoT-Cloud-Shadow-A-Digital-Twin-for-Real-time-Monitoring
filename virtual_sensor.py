import requests
import time
import random
import json

ENDPOINT_URL = "http://localhost:800/update-twin"
DEVICE_ID = "sensor_01"

def generate_temperature(current_temp):
    variation = random.uniform(-0.5, 0.5)
    return round(current_temp + variation, 2)

def run_virtual_sensor():
    current_temp = 22.0
    print(f"Starting Virtual Sensor")

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
            response = requests.post(ENDPOINT_URL, json=payload)
            print(f"Sent: {current_temp}°C | Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("Error: Backend is offline. Retrying")

        time.sleep(2)
    except KeyboardInterrupt:
        print("Sensor stopped by user")

if __name__ == "__main__":
    run_virtual_sensor()
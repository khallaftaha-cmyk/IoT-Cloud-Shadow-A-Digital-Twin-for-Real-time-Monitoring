import requests
import time
import json
import os

TWIN_API_URL = "http://localhost:8000/twin-status"

def get_twin_state():
    try:
        response = requests.get(TWIN_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def analyze(sensor_data):
    device = "sensor_01"

    data = sensor_data[device]
    temp = data['temperature']

    if temp > 25.0:
        return f"Critical: Overheating detected at {temp}°C! Immediate cooling required."
    elif temp > 23.0:
        return f"Warning: Temperature rising ({temp}°C). Monitor closely."
    else:
        return f"Nominal: System operating normally at {temp}°C."

def run_monitor():
    print("AI Monitor Initialized")
    print(f"Listening to Digital Twin at: {TWIN_API_URL}")

    while True:
        state = get_twin_state()

        if state:
            analysis = analyze(state)

            print(f"[{time.strftime('%H:%M:%S')}] {analysis}")
        
    time.sleep(5)

if __name__ == "__main__":
    run_monitor()

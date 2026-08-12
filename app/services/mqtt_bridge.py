import paho.mqtt.client as mqtt
import json
import asyncio
import requests
import os
import time

MQTT_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
API_URL = os.getenv("INTERNAL_API_URL", "http://localhost:8000")


class MQTTBridge:
    def __init__(self, host: str = MQTT_HOST, port: int = MQTT_PORT):
        self.host = host
        self.port = port
        self.client = mqtt.Client(client_id="digital_twin_mqtt_bridge")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self._running = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"[MQTT] Connected successfully to broker at {self.host}:{self.port}")
            # Subscribe to all device telemetry topics: iot/<device_id>/telemetry
            client.subscribe("iot/+/telemetry")
            print("[MQTT] Subscribed to topic 'iot/+/telemetry'")
        else:
            print(f"[MQTT] Connection failed with status code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic_parts = msg.topic.split("/")
            device_id = topic_parts[1] if len(topic_parts) >= 3 else payload.get("device_id", "unknown_device")

            if "device_id" not in payload:
                payload["device_id"] = device_id
            if "timestamp" not in payload:
                payload["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")

            print(f"[MQTT] Received telemetry from '{device_id}': {payload.get('temperature')}°C")

            # Forward telemetry to twin backend (internal call)
            # In a unified process, this can also invoke twin update directly
        except Exception as e:
            print(f"[MQTT] Error parsing message on '{msg.topic}': {e}")

    def start(self):
        try:
            print(f"[MQTT] Starting MQTT Bridge connecting to {self.host}:{self.port}...")
            self.client.connect_async(self.host, self.port, keepalive=60)
            self.client.loop_start()
            self._running = True
        except Exception as e:
            print(f"[MQTT] Failed to start MQTT client: {e}")

    def stop(self):
        if self._running:
            self.client.loop_stop()
            self.client.disconnect()
            self._running = False
            print("[MQTT] MQTT Bridge stopped")


mqtt_bridge = MQTTBridge()

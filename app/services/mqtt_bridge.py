import paho.mqtt.client as mqtt
import ssl
import json
import asyncio
import requests
import os
import time

MQTT_HOST = os.getenv("MQTT_BROKER_HOST", "a1tthoweuehg33-ats.iot.eu-north-1.amazonaws.com")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))
CERTS_DIR = os.getenv("MQTT_CERTS_DIR", r"C:\Users\DELL\Desktop\project\Iot monitor\certs")

CA_PATH = os.path.join(CERTS_DIR, "AmazonRootCA1.pem")
CERT_PATH = os.path.join(CERTS_DIR, "2635e4acfbd39cc96f8b38fdb5f89c730426506892c14375d429ed8df3241608-certificate.pem.crt")
KEY_PATH = os.path.join(CERTS_DIR, "2635e4acfbd39cc96f8b38fdb5f89c730426506892c14375d429ed8df3241608-private.pem.key")


class MQTTBridge:
    def __init__(self, host: str = MQTT_HOST, port: int = MQTT_PORT):
        self.host = host
        self.port = port
        self.client = mqtt.Client(client_id="digital_twin_mqtt_bridge")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self._running = False

        # Configure TLS if port 8883 (AWS IoT Core)
        if self.port == 8883 and os.path.exists(CA_PATH) and os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
            print(f"[MQTT] Configuring TLS certificates for AWS IoT Core at {self.host}...")
            self.client.tls_set(
                ca_certs=CA_PATH,
                certfile=CERT_PATH,
                keyfile=KEY_PATH,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"[MQTT] Connected successfully to MQTT Broker at {self.host}:{self.port}")
            client.subscribe("iot/+/telemetry")
            print("[MQTT] Subscribed to topic 'iot/+/telemetry'")
        else:
            print(f"[MQTT] Connection failed with return code {rc}")

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

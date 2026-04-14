import asyncio
import websockets
import json
import time
import os
import requests

BASE_URL = "http://localhost:8000"
TWIN_WS_BASE = "ws://localhost:8000/ws/twin-status"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

MONITOR_EMAIL = os.getenv("MONITOR_EMAIL", "monitor@twin.local")
MONITOR_PASSWORD = os.getenv("MONITOR_PASSWORD", "monitor_password")

SYSTEM_PROMPT = """You are an AI monitoring agent for an IoT digital twin system.
You receive real-time sensor data and must analyze it for anomalies, trends, and risks.

Your response must always follow this exact format:
STATUS: <NOMINAL | WARNING | CRITICAL>
ANALYSIS: <one sentence describing what you observe>
ACTION: <one sentence recommending what to do, or 'No action required'>

Be concise. Do not add any extra text outside this format."""


def get_token() -> str:
    response = requests.post(
        f"{BASE_URL}/login",
        data={"username": MONITOR_EMAIL, "password": MONITOR_PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"[AUTH] Token acquired for '{MONITOR_EMAIL}'")
        return token
    raise RuntimeError(f"Login failed: {response.status_code} {response.text}")


def analyze_with_claude(sensor_data: dict) -> str:
    user_message = f"""Analyze the following digital twin sensor data and detect any anomalies:

{json.dumps(sensor_data, indent=2)}

Respond strictly in the required format."""

    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 200,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}]
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["content"][0]["text"].strip()
    raise RuntimeError(f"Claude API error {response.status_code}: {response.text}")


def format_output(analysis: str) -> str:
    lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
             for line in analysis.splitlines() if ":" in line}

    status = lines.get("STATUS", "UNKNOWN")
    icons = {"NOMINAL": "✓", "WARNING": "⚠", "CRITICAL": "✖", "UNKNOWN": "?"}
    icon = icons.get(status, "?")

    output = f"[{time.strftime('%H:%M:%S')}] {icon} {status}"
    if "ANALYSIS" in lines:
        output += f"\n  → {lines['ANALYSIS']}"
    if "ACTION" in lines:
        output += f"\n  → {lines['ACTION']}"
    return output


async def monitor():
    print("=" * 50)
    print("  Claude AI Monitor — Digital Twin System")
    print("=" * 50)
    print(f"  Model    : claude-opus-4-5")
    print(f"  Mode     : WebSocket (event-driven)")
    print("=" * 50)

    if not ANTHROPIC_API_KEY:
        print("\n[ERROR] ANTHROPIC_API_KEY is not set.\n")
        return

    while True:
        try:
            token = get_token()
            ws_url = f"{TWIN_WS_BASE}?token={token}"

            async with websockets.connect(ws_url) as ws:
                print(f"\n[WS] Connected and authenticated\n")

                async for raw_message in ws:
                    message = json.loads(raw_message)

                    if message.get("event") == "connected":
                        print("[WS] Handshake complete. Listening for updates...\n")
                        continue

                    if message.get("event") == "twin_update":
                        payload = {message["device_id"]: message["data"]}
                        try:
                            analysis = analyze_with_claude(payload)
                            print(format_output(analysis))
                            print()
                        except Exception as e:
                            print(f"[{time.strftime('%H:%M:%S')}] Analysis failed: {e}\n")

        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"[WS] Connection lost: {e}. Retrying in 5s...\n")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[WS] Error: {e}. Retrying in 5s...\n")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(monitor())
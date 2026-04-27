"""
ws_client.py — Test client for the digital twin WebSocket endpoint.
Run this to verify the WebSocket connection independently of the AI monitor.

Usage:
    python ws_client.py
"""

import asyncio
import websockets
import json
from datetime import datetime

TWIN_WS_URL = "ws://localhost:8000/ws/twin-status"


def pretty_print(message: dict):
    event = message.get("event", "unknown")
    timestamp = datetime.now().strftime("%H:%M:%S")

    if event == "connected":
        print(f"[{timestamp}] ✓ Connected — current state:")
        print(json.dumps(message.get("current_state", {}), indent=4))

    elif event == "twin_update":
        device = message.get("device_id", "unknown")
        data = message.get("data", {})
        temp = data.get("temperature", "N/A")
        status = data.get("status", "N/A")
        last_seen = data.get("last_seen", "N/A")
        print(f"[{timestamp}] Update — {device} | {temp}°C | {status} | {last_seen}")

    else:
        print(f"[{timestamp}] Unknown event: {json.dumps(message, indent=2)}")


async def listen():
    print("=" * 50)
    print("  WebSocket Test Client — Digital Twin")
    print("=" * 50)
    print(f"  Connecting to: {TWIN_WS_URL}")
    print("  Press Ctrl+C to stop")
    print("=" * 50 + "\n")

    while True:
        try:
            async with websockets.connect(TWIN_WS_URL) as ws:
                async for raw_message in ws:
                    message = json.loads(raw_message)
                    pretty_print(message)

        except (websockets.ConnectionClosed, ConnectionRefusedError):
            print("\n[WS] Connection lost. Retrying in 5s...")
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("\n[WS] Stopped by user.")
            break


if __name__ == "__main__":
    asyncio.run(listen())
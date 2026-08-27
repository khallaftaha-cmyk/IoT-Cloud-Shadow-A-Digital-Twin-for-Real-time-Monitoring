from fastapi import status, Depends, WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio

from .. import database, models, schemas
from . import oauth2
from ..services.alert_engine import evaluate_telemetry

twin_state = {
    "sensor_01": {
        "temperature": 22.0,
        "humidity": 45.0,
        "pressure": 1013.2,
        "battery_level": 98.0,
        "status": "online",
        "last_seen": "N/A"
    }
}

router = APIRouter(tags=["Twin"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


@router.post("/update-twin", status_code=status.HTTP_201_CREATED, response_model=schemas.DataOut)
async def update_twin(
    data: schemas.DataIn,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Update digital twin state, persist sensor reading to Postgres, evaluate alert rules,
    and broadcast real-time updates over WebSockets.
    """
    state_payload = {
        "temperature": data.temperature,
        "humidity": data.humidity,
        "pressure": data.pressure,
        "battery_level": data.battery_level,
        "status": data.status,
        "extra_metadata": data.extra_metadata,
        "last_seen": data.timestamp.isoformat()
    }
    twin_state[data.device_id] = state_payload

    # Persist to Postgres database
    new_reading = models.SensorReading(
        device_id=data.device_id,
        temperature=data.temperature,
        humidity=data.humidity,
        pressure=data.pressure,
        battery_level=data.battery_level,
        status=data.status,
        extra_metadata=data.extra_metadata,
        timestamp=data.timestamp
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    # Evaluate rules engine for alerts
    alerts = evaluate_telemetry(data, db)
    for alert in alerts:
        await manager.broadcast({
            "event": "alert_triggered",
            "alert_id": alert.id,
            "device_id": alert.device_id,
            "metric": alert.metric,
            "value": alert.value,
            "threshold": alert.threshold,
            "severity": alert.severity,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat()
        })

    # Broadcast telemetry update over WebSocket
    await manager.broadcast({
        "event": "twin_update",
        "device_id": data.device_id,
        "data": twin_state[data.device_id]
    })

    return new_reading


@router.get("/twin-status")
def get_twin_status(
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Get full digital twin state map across all active devices.
    """
    return twin_state


@router.get("/devices")
def list_devices(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    List known devices and their current twin state.
    """
    devices = list(twin_state.keys())
    return {"devices": devices, "twin_state": twin_state}


@router.get("/history", response_model=list[schemas.DataOut])
def get_history(
    limit: int = 10,
    device_id: str = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Fetch historical telemetry readings.
    """
    query = db.query(models.SensorReading)
    if device_id:
        query = query.filter(models.SensorReading.device_id == device_id)
    readings = query.order_by(models.SensorReading.timestamp.desc()).limit(limit).all()
    return readings


@router.websocket("/ws/twin-status")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = None,
    db: Session = Depends(database.get_db),
):
    """
    WebSocket endpoint for real-time telemetry streaming, alerts, and actuation notifications.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if token:
        try:
            token_data = oauth2.verify_access_token(token, credentials_exception)
            user = db.query(models.User).filter(models.User.id == token_data.id).first()
            if not user:
                await websocket.close(code=1008)
                return
        except HTTPException:
            await websocket.close(code=1008)
            return

    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({
            "event": "connected",
            "message": "Subscribed to digital twin updates",
            "current_state": twin_state
        }))
        # Send a ping every 25s so nginx proxy_read_timeout (60s) is never hit.
        # The browser ignores unknown event types gracefully.
        ping_counter = 0
        while True:
            await asyncio.sleep(1)
            ping_counter += 1
            if ping_counter >= 25:
                ping_counter = 0
                try:
                    await websocket.send_text(json.dumps({"event": "ping"}))
                except Exception:
                    break  # client gone, clean up below
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
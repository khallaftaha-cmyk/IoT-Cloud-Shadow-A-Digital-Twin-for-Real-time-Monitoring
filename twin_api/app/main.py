from fastapi import FastAPI, status, HTTPException, Depends, WebSocket, WebSocketDisconnect
from . import schemas, database, models
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio

twin_state = {
    "sensor_01": {"temperature": "N/A", "status": "offline", "last_seen": "N/A"}
}

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
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
            self.active_connections.remove(conn)


manager = ConnectionManager()


@app.post("/update-twin", status_code=status.HTTP_201_CREATED, response_model=schemas.DataOut)
async def update_twin(data: schemas.DataIn, db: Session = Depends(database.get_db)):
    twin_state[data.device_id] = {
        "temperature": data.temperature,
        "status": data.status,
        "last_seen": data.timestamp.isoformat()
    }

    new_reading = models.SensorReading(**data.dict())
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    await manager.broadcast({
        "event": "twin_update",
        "device_id": data.device_id,
        "data": twin_state[data.device_id]
    })

    return new_reading


@app.get("/twin-status")
def get_twin_status():
    return twin_state


@app.get("/history", response_model=list[schemas.DataIn])
def get_history(limit: int = 10, db: Session = Depends(database.get_db)):
    readings = db.query(models.SensorReading).order_by(
        models.SensorReading.timestamp.desc()
    ).limit(limit).all()
    return readings


@app.websocket("/ws/twin-status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({
            "event": "connected",
            "message": "Subscribed to digital twin updates",
            "current_state": twin_state
        }))
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
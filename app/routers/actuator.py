from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import json

from .. import database, models, schemas
from . import oauth2
from .twin import manager

router = APIRouter(prefix="/actuate", tags=["Actuation"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ActuatorCommandOut)
async def send_actuator_command(
    command_in: schemas.ActuatorCommandIn,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Issue an actuation command to a remote IoT device or digital twin.
    """
    new_command = models.ActuatorCommand(
        device_id=command_in.device_id,
        command=command_in.command,
        params=command_in.params,
        status="pending",
        issued_by=current_user.id,
        issued_at=datetime.now(timezone.utc)
    )
    db.add(new_command)
    db.commit()
    db.refresh(new_command)

    # Broadcast actuation event to WebSocket clients
    await manager.broadcast({
        "event": "actuator_command",
        "command_id": new_command.id,
        "device_id": new_command.device_id,
        "command": new_command.command,
        "params": new_command.params,
        "status": new_command.status,
        "issued_at": new_command.issued_at.isoformat()
    })

    return new_command


@router.get("/history", response_model=List[schemas.ActuatorCommandOut])
def get_actuation_history(
    device_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Retrieve actuation command history.
    """
    query = db.query(models.ActuatorCommand)
    if device_id:
        query = query.filter(models.ActuatorCommand.device_id == device_id)

    commands = query.order_by(models.ActuatorCommand.issued_at.desc()).limit(limit).all()
    return commands


@router.get("/pending/{device_id}", response_model=List[schemas.ActuatorCommandOut])
def get_pending_commands(
    device_id: str,
    db: Session = Depends(database.get_db),
):
    """
    Fetch pending commands for a specific device (polling interface for edge hardware).
    """
    commands = db.query(models.ActuatorCommand).filter(
        models.ActuatorCommand.device_id == device_id,
        models.ActuatorCommand.status == "pending"
    ).all()
    return commands


@router.patch("/{command_id}/status", response_model=schemas.ActuatorCommandOut)
async def update_command_status(
    command_id: int,
    status_update: schemas.ActuatorStatusUpdate,
    db: Session = Depends(database.get_db),
):
    """
    Acknowledge or update execution status of an actuation command.
    """
    command = db.query(models.ActuatorCommand).filter(models.ActuatorCommand.id == command_id).first()
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")

    command.status = status_update.status
    if status_update.status in ["acknowledged", "executed"]:
        command.acknowledged_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(command)

    await manager.broadcast({
        "event": "actuator_status_update",
        "command_id": command.id,
        "device_id": command.device_id,
        "status": command.status
    })

    return command

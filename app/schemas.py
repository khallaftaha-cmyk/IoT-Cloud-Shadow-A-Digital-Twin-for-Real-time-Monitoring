from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List

class DataIn(BaseModel):
    device_id: str
    temperature: float
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    battery_level: Optional[float] = None
    status: str
    extra_metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


class DataOut(BaseModel):
    id: int
    device_id: str
    temperature: float
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    battery_level: Optional[float] = None
    status: str
    extra_metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


class UserIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


# Actuation Schemas
class ActuatorCommandIn(BaseModel):
    device_id: str
    command: str  # e.g., COOLING_ON, HEATING_OFF, SET_SPEED, EMERGENCY_SHUTDOWN
    params: Optional[Dict[str, Any]] = None


class ActuatorCommandOut(BaseModel):
    id: int
    device_id: str
    command: str
    params: Optional[Dict[str, Any]] = None
    status: str
    issued_by: Optional[int] = None
    issued_at: datetime
    acknowledged_at: Optional[datetime] = None


class ActuatorStatusUpdate(BaseModel):
    status: str  # acknowledged, executed, failed


# Alert Rule Schemas
class AlertRuleIn(BaseModel):
    device_id: str
    metric: str  # temperature, humidity, pressure, battery_level
    operator: str  # >, <, >=, <=, ==
    threshold: float
    severity: Optional[str] = "warning"  # warning, critical


class AlertRuleOut(BaseModel):
    id: int
    device_id: str
    metric: str
    operator: str
    threshold: float
    severity: str
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime


class AlertOut(BaseModel):
    id: int
    rule_id: Optional[int] = None
    device_id: str
    metric: str
    value: float
    threshold: float
    severity: str
    message: str
    acknowledged: bool
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None

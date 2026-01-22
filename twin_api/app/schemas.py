from pydantic import BaseModel
from datetime import datetime

class DataIn(BaseModel):
    device_id: str
    temperature: float
    status: str
    timestamp: datetime

class DataOut(BaseModel):
    id: int
    device_id: str
    temperature: float
    status: str
    timestamp: datetime



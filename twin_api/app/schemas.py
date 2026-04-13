from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

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



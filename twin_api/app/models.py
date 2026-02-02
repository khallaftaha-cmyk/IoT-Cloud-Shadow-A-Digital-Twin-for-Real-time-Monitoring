from .database import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

class SensorReading(Base):
    __tablename__ = "Sensor_Data"

    id = Column(Integer, primary_key = True, nullable = False)
    device_id = Column(String, nullable = False)
    temperature  = Column(Float, nullable = False)
    status  = Column(String, nullable = False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))
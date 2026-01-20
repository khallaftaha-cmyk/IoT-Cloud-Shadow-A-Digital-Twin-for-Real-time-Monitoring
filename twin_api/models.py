from .database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

class Post(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key = True, nullable = False)
    device_id = Column(String, server_default = 'True', nullable = False)
    current_temp  = Column(Float, nullable = False)
    status  = Column(String, nullable = False)
    timstamp = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))
from .database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class SensorReading(Base):
    __tablename__ = "Sensor_Data"

    id = Column(Integer, primary_key=True, nullable=False)
    device_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    battery_level = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    extra_metadata = Column(JSON, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class ActuatorCommand(Base):
    __tablename__ = "actuator_commands"

    id = Column(Integer, primary_key=True, nullable=False)
    device_id = Column(String, nullable=False)
    command = Column(String, nullable=False)
    params = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending, acknowledged, executed, failed
    issued_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    issued_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    acknowledged_at = Column(TIMESTAMP(timezone=True), nullable=True)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, nullable=False)
    device_id = Column(String, nullable=False)
    metric = Column(String, nullable=False)  # temperature, humidity, pressure, battery_level
    operator = Column(String, nullable=False)  # >, <, >=, <=, ==
    threshold = Column(Float, nullable=False)
    severity = Column(String, nullable=False, default="warning")  # warning, critical
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, nullable=False)
    rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True)
    device_id = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    acknowledged = Column(Boolean, nullable=False, default=False)
    triggered_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    acknowledged_at = Column(TIMESTAMP(timezone=True), nullable=True)
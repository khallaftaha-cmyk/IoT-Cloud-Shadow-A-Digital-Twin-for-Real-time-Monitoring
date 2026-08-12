from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int 
    anthropic_api_key: str = ""  

    # Redis — used for persistent twin state (replaces in-memory dict)
    redis_url: str = "redis://localhost:6379/0"

    # MQTT — used for hardware device ingestion bridge
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883

    class Config:
        env_file = ".env"

settings = Settings()
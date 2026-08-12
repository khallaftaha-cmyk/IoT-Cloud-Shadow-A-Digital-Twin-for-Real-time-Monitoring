from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import auth, twin, user, actuator, alerts
from .services.mqtt_bridge import mqtt_bridge


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle: Start MQTT Bridge
    try:
        mqtt_bridge.start()
    except Exception as e:
        print(f"[LIFESPAN] MQTT Bridge startup warning: {e}")
    yield
    # Shutdown lifecycle: Stop MQTT Bridge
    try:
        mqtt_bridge.stop()
    except Exception as e:
        print(f"[LIFESPAN] MQTT Bridge shutdown warning: {e}")


app = FastAPI(title="Digital Twin IoT System", version="2.0.0", lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(twin.router)
app.include_router(actuator.router)
app.include_router(alerts.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "2.0.0"}

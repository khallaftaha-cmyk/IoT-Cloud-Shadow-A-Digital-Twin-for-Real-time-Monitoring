from fastapi import FastAPI, status, HTTPException, Depends
from . import schemas, database, models
from sqlalchemy.orm import Session

twin_state = {
    "sensor_01":{"temperature":"N/A", "status":"offline", "last_seen":"N/A"}
}

app = FastAPI()

@app.post("/update-twin", status_code=status.HTTP_201_CREATED, response_model=schemas.DataOut)
def update_twin(data:schemas.DataIn, db:Session = Depends(database.get_db)):
    twin_state[data.device_id] = {
        "temperature": data.temperature,
        "status": data.status,
        "last_seen": data.timestamp
    }

    new_reading = models.SensorReading(**data.dict())
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading


@app.get("/twin-status")
def get_twin_status():

    return twin_state

@app.get("/history", response_model=list[schemas.DataIn])
def get_history(limit: int = 10, db:Session = Depends(database.get_db)):

    readings = db.query(models.SensorReading).order_by(models.SensorReading.timestamp.desc()).limit(limit).all()

    return readings
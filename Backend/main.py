from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from detector import classify

app = FastAPI()

# Path to the Frontend folder, worked out from where this file lives.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "Frontend"

# Temporary memory: one combined record per zone.
# It disappears when the server restarts.
latest_readings = {}

# The values that come from the real sensors on the ESP32.
SENSOR_FIELDS = ["temperature", "humidity", "moisture"]


class Reading(BaseModel):
    """Any of these values may be sent. Values that are not sent stay unchanged."""
    zone: int = Field(default=1, ge=1, description="Zone number, starting from 1")
    temperature: float | None = Field(default=None, ge=-40, le=80, description="Air temperature in degrees Celsius (DHT22)")
    humidity: float | None = Field(default=None, ge=0, le=100, description="Air humidity in percent (DHT22)")
    moisture: float | None = Field(default=None, ge=0, le=100, description="Soil moisture in percent")
    flow: float | None = Field(default=None, ge=0, description="Water flow in litres per minute (simulated)")


@app.get("/")
def home():
    return {"message": "Drip irrigation server is running"}


@app.get("/dashboard")
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/reading")
def receive_reading(reading: Reading):
    if all(getattr(reading, name) is None for name in SENSOR_FIELDS + ["flow"]):
        raise HTTPException(status_code=400, detail="Send at least one reading value.")

    now = datetime.now().isoformat(timespec="seconds")

    # Get this zone's record, or create an empty one the first time.
    record = latest_readings.setdefault(reading.zone, {
        "zone": reading.zone,
        "temperature": None,
        "humidity": None,
        "moisture": None,
        "flow": None,
        "sensors_updated_at": None,
        "flow_updated_at": None,
        "verdict": {"status": "NO_SENSOR", "fault": None, "message": "Waiting for flow data."},
    })

    # Update only the values that were actually sent.
    if reading.flow is not None:
        record["flow"] = reading.flow
        record["flow_updated_at"] = now
        record["verdict"] = classify(reading.flow)

    for name in SENSOR_FIELDS:
        value = getattr(reading, name)
        if value is not None:
            record[name] = value
            record["sensors_updated_at"] = now

    return {"status": "received", "reading": record}


@app.get("/zones")
def get_zones():
    return latest_readings
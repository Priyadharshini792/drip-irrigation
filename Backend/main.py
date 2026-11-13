from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from detector import classify

app = FastAPI()

# Path to the Frontend folder, worked out from where this file lives.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "Frontend"

# Temporary memory: the latest reading for each zone.
# It disappears when the server restarts. We'll add a real database later.
latest_readings = {}


class Reading(BaseModel):
    """The shape of data we accept from the ESP32."""
    zone: int = Field(default=1, ge=1, description="Zone number, starting from 1")
    temperature: float = Field(ge=-40, le=80, description="Air temperature in degrees Celsius (DHT11)")
    humidity: float = Field(ge=0, le=100, description="Air humidity in percent (DHT11)")
    flow: float = Field(ge=0, description="Water flow in litres per minute")
    moisture: float = Field(ge=0, le=100, description="Soil moisture in percent")


@app.get("/")
def home():
    return {"message": "Drip irrigation server is running"}


@app.get("/dashboard")
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/reading")
def receive_reading(reading: Reading):
    data = reading.model_dump()
    data["received_at"] = datetime.now().isoformat(timespec="seconds")
    data["verdict"] = classify(reading.flow)
    latest_readings[reading.zone] = data
    return {"status": "received", "reading": data}


@app.get("/zones")
def get_zones():
    return latest_readings
import json
import random
import time
import urllib.request

# Where the server listens for readings.
URL = "http://127.0.0.1:8000/reading"


def make_reading():
    """Build one fake reading with small random changes, like a real sensor."""
    return {
        "temperature": round(random.uniform(28.0, 32.0), 1),
        "humidity": round(random.uniform(55.0, 70.0), 1),
        "flow": round(random.uniform(2.3, 2.7), 2),
        "moisture": round(random.uniform(38.0, 44.0), 1),
    }


def send(reading):
    """POST one reading to the server and return the HTTP status code."""
    body = json.dumps(reading).encode("utf-8")
    request = urllib.request.Request(
        URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.status


print("Simulator started. Press Ctrl+C to stop.")

while True:
    reading = make_reading()
    try:
        status = send(reading)
        print("Sent:", reading, "-> HTTP", status)
    except Exception as error:
        print("Could not send. Is the server running?", error)
    time.sleep(2)
import json
import re
import sys
import urllib.request

import serial  # this comes from the "pyserial" package

# ---------- EDIT THIS ----------
COM_PORT = "COM5"   # the port name from the previous step
# -------------------------------

BAUD_RATE = 115200  # must match Serial.begin(115200) in the ESP32 code
URL = "http://127.0.0.1:8000/reading"


def number_in(text):
    """Return the first number in the text, or None (for example for 'Sensor Error')."""
    match = re.search(r"-?\d+(\.\d+)?", text)
    return float(match.group()) if match else None


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


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else COM_PORT

    try:
        connection = serial.Serial(port, BAUD_RATE, timeout=2)
    except serial.SerialException as error:
        print("Could not open", port)
        print("Is the Arduino Serial Monitor still open? Is the port name right?")
        print(error)
        return

    print("Reading from", port, "- press Ctrl+C to stop.")
    reading = {}

    while True:
        line = connection.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue

        # The ESP32 prints one block of lines per cycle. Collect the values as they arrive.
        if line.startswith("Soil Moisture:"):
            value = number_in(line.split(":", 1)[1])
            if value is not None:
                reading["moisture"] = value
        elif line.startswith("Temperature:"):
            value = number_in(line.split(":", 1)[1])
            if value is not None:
                reading["temperature"] = value
        elif line.startswith("Humidity:"):
            value = number_in(line.split(":", 1)[1])
            if value is not None:
                reading["humidity"] = value
        elif line.startswith("Pump Status:"):
            # "Pump Status" is the last line of each block, so the reading is complete.
            if reading:
                try:
                    status = send(reading)
                    print("Sent:", reading, "-> HTTP", status)
                except Exception as error:
                    print("Could not send. Is the server running?", error)
            reading = {}


main()
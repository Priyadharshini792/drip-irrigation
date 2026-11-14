import json
import msvcrt
import random
import sys
import time
import urllib.request

# Where the server listens for readings.
URL = "http://127.0.0.1:8000/reading"

# Each mode: a name to print, and the lowest and highest flow (litres per minute) it produces.
MODES = {
    "normal": ("Normal flow", 2.3, 2.7),
    "blocked": ("Blocked emitter (low flow)", 0.9, 1.3),
    "leak": ("Leak (high flow)", 3.4, 3.9),
    "noflow": ("No flow", 0.0, 0.0),
}

# Which key switches to which mode.
KEYS = {"1": "normal", "2": "blocked", "3": "leak", "4": "noflow"}


def make_reading(mode):
    """Only the flow is simulated. The other values come from the real sensors."""
    _, low, high = MODES[mode]
    return {"flow": round(random.uniform(low, high), 2)}


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


def check_keyboard(mode):
    """If a mode key was pressed, switch to that mode."""
    while msvcrt.kbhit():
        key = msvcrt.getwch()
        if key in KEYS:
            mode = KEYS[key]
            print(">>> Mode changed to:", MODES[mode][0])
    return mode


mode = "normal"
if len(sys.argv) > 1 and sys.argv[1] in MODES:
    mode = sys.argv[1]

print("Flow simulator started in mode:", MODES[mode][0])
print("Keys: 1 = normal, 2 = blocked, 3 = leak, 4 = no flow. Press Ctrl+C to stop.")

while True:
    reading = make_reading(mode)
    try:
        status = send(reading)
        print("Sent:", reading, "-> HTTP", status)
    except Exception as error:
        print("Could not send. Is the server running?", error)

    # Wait about 2 seconds, but keep listening for key presses.
    for _ in range(20):
        time.sleep(0.1)
        mode = check_keyboard(mode)
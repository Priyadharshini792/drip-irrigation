# The flow we expect when everything is healthy, in litres per minute.
# This is a placeholder. We will measure the real value with the real hardware.
EXPECTED_FLOW = 2.5

LOW_FLOW_RATIO = 0.6    # below 60% of expected = low flow
HIGH_FLOW_RATIO = 1.3   # above 130% of expected = high flow
NO_FLOW_LIMIT = 0.1     # below this many L/min = no flow at all


def classify(flow):
    """Look at the water flow and return a verdict."""
    percent = round(flow / EXPECTED_FLOW * 100)

    if flow < NO_FLOW_LIMIT:
        return {
            "status": "FAULT",
            "fault": "NO_FLOW",
            "message": "No water is flowing. Check the pump, the tank and the tubing.",
        }

    if flow < EXPECTED_FLOW * LOW_FLOW_RATIO:
        return {
            "status": "FAULT",
            "fault": "LOW_FLOW",
            "message": f"Flow is only {percent}% of normal. Possible blocked emitter or clogged filter.",
        }

    if flow > EXPECTED_FLOW * HIGH_FLOW_RATIO:
        return {
            "status": "FAULT",
            "fault": "HIGH_FLOW",
            "message": f"Flow is {percent}% of normal. Possible leak or burst pipe.",
        }

    return {
        "status": "OK",
        "fault": None,
        "message": "Water flow is normal.",
    }
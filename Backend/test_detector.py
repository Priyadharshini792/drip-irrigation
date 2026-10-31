from detector import classify

# Each case is (flow in L/min, the verdict we expect).
cases = [
    (2.5, "OK"),
    (2.0, "OK"),
    (3.0, "OK"),
    (1.2, "LOW_FLOW"),
    (0.0, "NO_FLOW"),
    (3.6, "HIGH_FLOW"),
]

all_passed = True
for flow, expected in cases:
    result = classify(flow)
    got = result["fault"] or "OK"
    passed = got == expected
    if not passed:
        all_passed = False
    print("PASS" if passed else "FAIL", "| flow", flow, "->", got, "|", result["message"])

print()
print("All tests passed!" if all_passed else "Some tests FAILED.")
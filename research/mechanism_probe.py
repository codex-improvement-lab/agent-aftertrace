"""Synthetic research probe, not a product or an agent-benefit benchmark."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

root = Path(__file__).resolve().parent
target = root / "late_failure.py"
original = target.read_bytes()
events = []
previous_lines = {}
watched = ("balance", "step", "violation_seen")


def capture(frame, event, argument):
    if Path(frame.f_code.co_filename).resolve() != target:
        return None
    if event == "line" and frame.f_code.co_name == "settle":
        values = {
            name: frame.f_locals[name]
            for name in watched
            if name in frame.f_locals
            and type(frame.f_locals[name]) in (int, bool, float, str, type(None))
        }
        if not events or values != events[-1]["values"]:
            events.append({
                "eventId": len(events) + 1,
                "source": target.name,
                "frame": "settle",
                "observedBeforeLine": frame.f_lineno,
                "previousExecutedLine": previous_lines.get(id(frame)),
                "values": values,
            })
        previous_lines[id(frame)] = frame.f_lineno
    return capture


failure = None
final_locals = {}
try:
    sys.settrace(capture)
    runpy.run_path(str(target), run_name="__main__")
except AssertionError as error:
    failure = type(error).__name__
    trace = error.__traceback__
    while trace:
        if trace.tb_frame.f_code.co_name == "settle":
            final_locals = {name: trace.tb_frame.f_locals[name] for name in watched}
        trace = trace.tb_next
finally:
    sys.settrace(None)

first_negative = next(e for e in events if e["values"].get("balance", 0) < 0)
assert failure == "AssertionError"
assert final_locals["balance"] == 71
assert first_negative["values"]["balance"] == -33
assert first_negative["values"]["step"] == 47
assert first_negative["previousExecutedLine"] == 8
assert original == target.read_bytes()
payload = json.dumps(events, ensure_ascii=False, separators=(",", ":")).encode()
result = {
    "evidenceClass": "synthetic-local-mechanism-probe",
    "productImplemented": False,
    "agentSelectionMeasured": False,
    "competitorBenchmark": False,
    "targetRuns": 1,
    "sourceChanged": False,
    "sourceSha256": hashlib.sha256(original).hexdigest(),
    "terminalFailure": failure,
    "finalFrameValues": final_locals,
    "recordedChangeEvents": len(events),
    "rawTraceBytes": len(payload),
    "firstNegativeObservation": first_negative,
    "limitations": [
        "Only explicitly selected scalar locals in a synchronous toy program were captured.",
        "Observed location and previous executed line are not an automatic root-cause proof.",
        "No overhead, real model, real user, or competitor comparison was measured.",
    ],
}
# Locate the already created research evidence directory explicitly in this workspace.
destination = root / "results"
destination.mkdir(parents=True, exist_ok=True)
(destination / "postrun-watch-mechanism.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
)
(destination / "scalar-trace.json").write_bytes(payload + b"\n")
print(json.dumps(result, ensure_ascii=False, indent=2))

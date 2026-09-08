"""Reproduce the baseline disconfirmation and the query integration."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

from viz_query_baseline import first_negative_integer, observations

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aftertrace.query import Trace


def main():
    target = ROOT / "research" / "late_failure.py"
    output = ROOT / "research" / "results"
    output.mkdir(exist_ok=True)
    before = target.read_bytes()
    recording = output / "preflight-recording.json"
    process = subprocess.run([
        sys.executable, "-m", "viztracer", "--quiet", "--ignore_c_function",
        "--ignore_multiprocess", "--tracer_entries", "10000",
        "--include_files", str(target), "--log_var", "^(balance|step|violation_seen)$",
        "-o", str(recording), "--", str(target)
    ], capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30)
    assert process.returncode == 1
    assert b"AssertionError: a negative balance was observed earlier" in process.stderr
    baseline = first_negative_integer(recording, "balance")
    assert baseline["value"] == -33
    earlier_steps = [text for event, text in observations(recording, "step")
                     if event["ts"] <= baseline["timestampUs"]]
    assert earlier_steps[-1] == "47"
    assert target.read_bytes() == before
    result, exit_code = Trace(recording).first("balance", "lt", 0, None, None, None)
    assert exit_code == 0 and result["match"]["scalarValue"] == -33
    report = {
        "schema": "aftertrace-preflight/1",
        "evidenceClass": "synthetic-baseline-disconfirmation",
        "viztracerVersion": importlib.metadata.version("viztracer"),
        "sourceSha256": hashlib.sha256(before).hexdigest(),
        "protocolSha256": hashlib.sha256((ROOT / "research/PREFLIGHT_PROTOCOL.md").read_bytes()).hexdigest(),
        "targetExecutions": 1, "sourceChanged": False,
        "targetExitCode": 1, "recordingBytes": recording.stat().st_size,
        "baselineFirstNegative": baseline["value"], "precedingRecordedStep": 47,
        "aftertraceFirstNegative": result["match"]["scalarValue"],
        "newRecorderRequiredForThisFact": False,
        "agentSelectionMeasured": False, "wholeTaskBenefitMeasured": False,
        "m0StandaloneGate": "NOT_PASSED",
        "decision": "Publish only an experimental query integration; retain the standalone gate.",
    }
    (output / "preflight.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()


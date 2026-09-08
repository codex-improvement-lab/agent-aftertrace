"""Freeze first, then verify query compatibility on pinned library source.

No timing comparison, model invocation, or debugging success claim is made.
Baseline and Aftertrace consume the SAME VizTracer recording.
"""
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from compatibility_cases import CASES
from viz_query_baseline import observations

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aftertrace.query import Trace


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest():
    cases = []
    for case in CASES:
        version = importlib.metadata.version(case["package"])
        if version != case["version"]:
            raise RuntimeError(f"Install the pinned {case['package']} version first")
        source = Path(importlib.util.find_spec(case["module"]).origin)
        cases.append({**case, "sourceSha256": sha(source)})
    return {"schema": "aftertrace-library-compatibility/1",
            "evidenceClass": "authored-pinned-library-behavior-checks",
            "casesSourceSha256": sha(ROOT / "research/compatibility_cases.py"),
            "baselineSourceSha256": sha(ROOT / "research/viz_query_baseline.py"),
            "cases": cases}


def main():
    root = ROOT / "research/results"
    root.mkdir(exist_ok=True)
    frozen = root / "compatibility-v2-freeze.json"
    if sys.argv[1:] == ["--freeze"]:
        if frozen.exists():
            raise RuntimeError("Freeze already exists; retain it and explicitly version any new protocol.")
        frozen.write_text(json.dumps(manifest(), indent=2) + "\n", encoding="utf-8")
        print("Frozen 8 authored compatibility checks. These are not the M0 agent tasks.")
        return
    if sys.argv[1:]:
        raise RuntimeError("Use --freeze once, then run without arguments.")
    if json.loads(frozen.read_text()) != manifest():
        raise RuntimeError("Frozen inputs changed. No measurements run.")
    results = []
    for case in CASES:
        source = Path(importlib.util.find_spec(case["module"]).origin)
        before = sha(source)
        target = ROOT / "research/compatibility_cases.py"
        recording = root / (case["id"] + ".json")
        # A fresh pycache prefix ensures imported source passes through the
        # upstream AST instrumentation, instead of reading existing bytecode.
        with tempfile.TemporaryDirectory(prefix="aftertrace-pycache-") as cache:
            env = {**os.environ, "PYTHONPYCACHEPREFIX": cache,
                   "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
            process = subprocess.run([
                sys.executable, "-m", "viztracer", "--quiet", "--ignore_c_function",
                "--ignore_multiprocess", "--tracer_entries", "50000",
                "--include_files", str(source), "--log_var", "^" + re.escape(case["variable"]) + "$",
                "-o", str(recording), "--", str(target), case["id"]
            ], capture_output=True, env=env, timeout=60)
        row = {"id": case["id"], "targetExitCode": process.returncode,
               "sourceUnchanged": before == sha(source), "sourceSha256": before}
        if process.returncode:
            (root / (case["id"] + ".stderr.txt")).write_bytes(process.stderr)
            row["status"] = "target_failed"
        elif not recording.exists():
            row["status"] = "no_recording"
        else:
            baseline = [representation for _, representation in observations(recording, case["variable"])]
            trace = Trace(recording)
            selected = trace.select(case["variable"])
            recorded = [item.representation for item in selected]
            row.update({"baselineObservationCount": len(baseline), "aftertraceObservationCount": len(recorded),
                        "identicalObservationStream": baseline == recorded,
                        "expectedRepresentationsFound": all(value in recorded for value in case["expectedRepresentations"]),
                        "bufferOverflow": trace.overflow,
                        "recordingBytes": recording.stat().st_size})
            row["status"] = ("pass" if row["sourceUnchanged"] and row["identicalObservationStream"]
                             and row["expectedRepresentationsFound"] and trace.overflow is False else "fail")
        results.append(row)
        print(case["id"] + ": " + row["status"], flush=True)
    report = {
        "schema": "aftertrace-compatibility-results/1",
        "freezeSha256": sha(frozen),
        "environment": {"python": sys.version.split()[0], "platform": sys.platform,
                        "viztracer": importlib.metadata.version("viztracer")},
        "evidenceClass": "authored-pinned-library-behavior-checks",
        "agentTrials": 0, "wholeTaskComparisons": 0, "m0StandaloneGate": "NOT_PASSED",
        "results": results,
    }
    (root / "compatibility-v2-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not all(row["status"] == "pass" for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

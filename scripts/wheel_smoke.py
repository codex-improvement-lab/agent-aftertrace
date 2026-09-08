"""Validate distribution contents and query an installed wheel outside checkout."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import zipfile


def main():
    wheel = Path(sys.argv[1]).resolve()
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert all(name.startswith(("aftertrace/", "agent_aftertrace-0.1.0a1.dist-info/")) for name in names)
        assert all(not name.endswith((".pyc", ".env", ".json")) for name in names)
        assert "aftertrace/query.py" in names
        assert "aftertrace/cli.py" in names
    with tempfile.TemporaryDirectory(prefix="aftertrace-installed-") as folder:
        work = Path(folder)
        env_path = work / "venv"
        venv.create(env_path, with_pip=True)
        python = env_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = {key: value for key, value in os.environ.items()
               if key not in ("PYTHONPATH", "PYTHONHOME")}
        env["PYTHONIOENCODING"] = "utf-8"
        subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
                        "--no-deps", str(wheel)], cwd=work, env=env, check=True, capture_output=True)
        trace = work / "trace.json"
        trace.write_text(json.dumps({
            "viztracer_metadata": {"version": "1.1.1", "overflow": False},
            "traceEvents": [
                {"ph": "i", "pid": 1, "tid": 1, "ts": 1, "name": "Variable Assign - balance = -33"},
                {"ph": "i", "pid": 1, "tid": 1, "ts": 2, "name": "Variable Assign - balance = 71"},
            ]}), encoding="utf-8")
        before = trace.read_bytes()
        for invocation in ([str(python), "-m", "aftertrace"],
                           [str(env_path / ("Scripts/aftertrace.exe" if os.name == "nt" else "bin/aftertrace"))]):
            result = subprocess.run([*invocation, "first", str(trace), "--var", "balance",
                                     "--op", "lt", "--value", "0"], cwd=work, env=env,
                                    capture_output=True, text=True, check=True)
            payload = json.loads(result.stdout)
            assert payload["match"]["scalarValue"] == -33
            assert payload["coverage"]["captureCompleteness"] == "unknown"
            assert not result.stderr
        assert trace.read_bytes() == before
    print(json.dumps({"status": "pass", "wheel": wheel.name,
                      "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                      "packageFiles": len(names), "installedOutsideCheckout": True,
                      "moduleAndConsoleEntryPoints": True, "queryInputUnchanged": True}))


if __name__ == "__main__":
    main()


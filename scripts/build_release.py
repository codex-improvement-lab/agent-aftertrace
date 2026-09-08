"""Build with a commit-derived timestamp; source releases require a commit."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
timestamp = subprocess.check_output(["git", "log", "-1", "--format=%ct"], cwd=root, text=True).strip()
if not timestamp.isdigit():
    raise RuntimeError("A source commit is required before release packaging.")
subprocess.run([sys.executable, "-m", "build", "--sdist", "--wheel"],
               cwd=root, env={**os.environ, "SOURCE_DATE_EPOCH": timestamp}, check=True)


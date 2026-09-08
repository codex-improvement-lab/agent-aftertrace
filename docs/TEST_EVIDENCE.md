# Test evidence

Current local evidence: Windows, CPython 3.11.9, 2026-09-08.
Source and release-bound CI results are recorded in release/PUBLICATION.md
when verified. Hosted macOS CI is not a physical Mac agent workflow test.

## Reader behavior

The pytest suite covers scalar parsing without execution, no target imports,
file byte preservation, call/instant separation, stable trace IDs, pagination,
bounded input/output, ambiguous streams, overflow, unknown capture, malformed
data, opaque values, duplicate keys, timestamp ties, and actual CLI exit
codes. Initial run: **50 passed**.

## Synthetic baseline disconfirmation

`python research/preflight.py` records the existing late-failure example
using VizTracer 1.1.1, queries it with the independent small baseline and
Aftertrace, checks the source hash, and asserts both find -33.

One target execution, zero target source changes. The last recorded step
before the negative balance is 47. The same example's final balance is 71.
This demonstrates capture/query mechanics, not agent benefit.
See [the frozen protocol](../research/PREFLIGHT_PROTOCOL.md) and
[Windows result](evidence/preflight-windows.json).

## Eight pinned libraries

The authored cases inspect intermediate values in unmodified public
library code. They are **not historical bugs, blinded tasks or real-user
incidents**. Both readers consume exactly the same VizTracer file.

- First run: identical observed streams 8/8; expected-value assertions 7/8.
- The packaging oracle omitted the epoch `0!`. Both tools correctly returned
  the actual strings. The original result remains available.
- Corrected v2: identical observed streams 8/8; expected-value assertions 8/8;
  all eight source hashes unchanged; buffer overflow false in these runs.

[Original freeze](evidence/compatibility-v1-freeze.json),
[original results](evidence/compatibility-v1.json),
[oracle amendment](../research/COMPATIBILITY_AMENDMENT.md),
[v2 freeze](evidence/compatibility-v2-freeze.json),
[v2 results](evidence/compatibility-v2.json).

These results establish that the integration reads these captured facts
correctly. They do not show it is better than the baseline.

Reproduce in a fresh checkout:

```sh
python -m pip install -r research/requirements-compatibility.txt
python research/compatibility.py --freeze
python research/compatibility.py
```

The manifest freezes installed package versions, target source hashes,
case definitions and baseline code before capture. The runner refuses
changed frozen inputs. Fresh private pycache prefixes force source imports
through VizTracer's AST instrumentation; existing bytecode may otherwise
skip variable instrumentation. Raw recordings remain ignored local files.

## Not established

Actual independent agent trials: **0**.
Whole-task cost comparisons: **0**.
Headless mcp-debugger/PDB/Birdseye task comparisons: **not run**.
Agent discovery, installation, preference and repeat usage: **unmeasured**.
No claim of saved time, fewer debugging attempts or stronger root-cause
accuracy is supported. M0 remains NOT PASSED.

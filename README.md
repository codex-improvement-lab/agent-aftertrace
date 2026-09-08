# Aftertrace

**Ask a finished Python run about its recorded past.**

Small JSON queries over [VizTracer](https://github.com/gaogaotiantian/viztracer)
recordings, for coding agents investigating values that disappeared before
the final traceback.

**0.1.0a1 · experimental integration.** VizTracer records execution. Aftertrace
reads the saved JSON. No model API, server, or required UI. The query package
uses only the Python standard library; recording is an optional dependency.

## Try the complete loop

Python 3.11 or later, in a virtual environment:

```sh
git clone https://github.com/codex-improvement-lab/agent-aftertrace.git
cd agent-aftertrace
python -m pip install ".[record]"
python -m viztracer --quiet --ignore_c_function --ignore_multiprocess --tracer_entries 10000 --log_var "^(balance|step|violation_seen)$" -o result.json -- research/late_failure.py
python -m aftertrace first result.json --var balance --op lt --value 0
```

The recording command intentionally ends with `AssertionError` (exit 1).
Run the query afterward: it reads the saved recording without rerunning the
target. The demo finishes with balance 71; the query finds a recorded -33.
It is a synthetic demonstration, not a real bug benchmark.

Selected fields from the response:

```json
{
  "status": "found",
  "match": {"variable": "balance", "scalarValue": -33},
  "claim": "first_comparable_recorded_match_in_selected_stream",
  "rootCauseEstablished": false
}
```

To query an existing recording, install the wheel from
[Releases](https://github.com/codex-improvement-lab/agent-aftertrace/releases);
VizTracer is unnecessary in the query environment.

## The agent interface

```sh
aftertrace inspect result.json
aftertrace history result.json --var balance --offset 40 --limit 10
aftertrace first result.json --var balance --op lt --value 0
aftertrace calls result.json --limit 10
```

With a recording made using VizTracer's `--log_func_exec`, select an actual
call ID from `calls` and query its steps:

```sh
aftertrace history execution.json --var balance --call c2
aftertrace first execution.json --var balance --call c2 --op lt --value 0
```

`c2` is an example, not a stable ID across different recordings. IDs are
paired with the SHA-256 `traceId` returned in every successful query.

| Response | Meaning |
| --- | --- |
| `found` | A comparable recorded scalar matched in the selected stream. |
| `no_observed_match` | None of the selected comparable records matched. |
| `not_recorded` | That variable or stream has no usable observations. |
| `inconclusive` / `partial_match` | Missing buffer history, opaque values, malformed records, or tied ordering prevent the requested conclusion. |
| `ambiguous_stream` | Select a process/thread or a call before asking for a first match. |

Exit codes are 0 for results, 1 for no observed match, 2 for invalid input,
and 3 for insufficient or ambiguous evidence. Normal queries and errors
emit one JSON document; `--help` and `--version` emit text.
See the [query contract](docs/QUERY_CONTRACT.md).

An optional [Agent Skill](skills/aftertrace-query/SKILL.md) describes when to
use an existing recording and when to skip this tool. Publishing a Skill
does not automatically install it in agents or make them discover this repo.

## What the first experiment taught us

VizTracer plus our small [independent query script](research/viz_query_baseline.py)
already recovered the demo's lost value in one target run without source
changes. **Aftertrace is therefore an integration, not a new tracing engine.**

The reader also returned the same observations as that baseline in eight
pinned library checks: packaging, urllib3, python-dateutil, Click, Jinja2,
boltons, more-itertools, and jsonschema. These are authored behavior
investigations. They are not eight historical bugs or eight successful agent
trials. The first packaging oracle was wrong; we retained the original
7/8 result and documented its correction.

**Actual agent trials: 0. Whole-task cost comparisons: 0.**
We have not shown agent preference, saved debugging time, or superiority to
VizTracer scripts, PDB, Birdseye, or mcp-debugger.
Read [test evidence](docs/TEST_EVIDENCE.md) and the
[next-stage gate](docs/NEXT_STAGE.md).

## Recording limits matter

- Aftertrace cannot reconstruct values that were not recorded. An empty
  history does not prove a value never existed.
- Variable instant records have timestamps, but no reliable assignment line
  or call identity. Function steps have recorded lines and call identity,
  but no per-step timestamps. The tool keeps these streams separate.
- Values come from VizTracer's recorded `repr` text. Scalar decoding describes
  that text; it cannot verify an object's original runtime type.
- No buffer overflow does not establish full capture. Unobserved mutations,
  cached bytecode, filters, and unsupported instrumentation can still omit data.
- Recordings may contain source, paths and sensitive values. Recording can
  call object `__repr__` and affect execution. VizTracer filters are not a
  privacy sandbox; inspect scope and recording options before a real run.
  Its entry count is not a strict byte or memory budget.
- Querying is local and read-only, with no telemetry, network calls, target
  imports, or expression evaluation. Input is capped at 32 MiB; output is
  paginated and long representations are visibly truncated.

The tested producer is VizTracer 1.1.1. See its
[capture options](https://viztracer.readthedocs.io/en/stable/extra_log.html)
and [filters](https://viztracer.readthedocs.io/en/stable/filter.html).

## Development

```sh
python -m pip install ".[test,record]"
python -m pytest -q
python research/preflight.py
```

The eight-library check has separate pinned dependencies and a frozen
manifest. Instructions and platform evidence are in
[TEST_EVIDENCE.md](docs/TEST_EVIDENCE.md).

MIT for this repository. VizTracer is separately licensed under Apache-2.0.
No VizTracer source or third-party library source is vendored here.

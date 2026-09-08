# Aftertrace 0.1.0a1 — experimental VizTracer query integration

Ask a saved Python run about its recorded past.

This preview adds a small local interface for agents to inspect VizTracer
1.1.1 JSON: bounded variable history, first comparable scalar matches,
recorded calls and within-call assignments. Queries emit JSON with explicit
coverage and exit codes, without evaluating expressions or rerunning code.

VizTracer remains the recording engine. A competent small baseline script
already recovered the motivating demo's missing value. We are publishing an
integration to test whether easier access to recorded history is worth using.

Validation includes query contract tests, clean wheel installation, a
synthetic baseline comparison and authored checks against eight pinned Python
libraries. Those library checks are not historical bug repairs or agent
trials. The original packaging-oracle failure and its correction are public.

**Agent trials: 0. Whole-task cost comparisons: 0. Independent product M0:
NOT PASSED.** No claims of agent adoption, debugging time saved or superiority
to existing debuggers.

Python 3.11+. The reader itself uses only the standard library. Install the
wheel for existing recordings; install VizTracer 1.1.1 separately to record.
The source archive also includes the optional Agent Skill, examples and
reproducible research checks.

Read README.md, docs/QUERY_CONTRACT.md and docs/TEST_EVIDENCE.md before using
results to make conclusions. Trace files may contain sensitive source and
values; the tool does not upload them or guarantee they are sanitized.

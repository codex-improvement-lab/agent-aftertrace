# Preflight: test the proposed information advantage

Frozen before the first VizTracer run, 2026-09-08.

This is an early disconfirmation check, not the planned M0 agent benchmark.
The existing synthetic `late_failure.py` and its ground truth are unchanged:
terminal balance 71, first negative recorded balance -33 at step 47.

Run VizTracer 1.1.1 with its documented variable logging on the same source.
Allow a reusable Python JSON reader, ordinary documentation, and the same
watched variables. Check whether one recording, no target source changes, and
post-run queries recover the lost intermediate value. Record limitations in
location, invocation identity, value representation, and data completeness.
Do not infer whole-task time savings from query output size or API shape.

If the baseline recovers the fact, the claim that a new recorder is required
is rejected. Build only a small, explicitly attributed VizTracer query
integration for further experiments. Publishing such an experimental helper
does not pass or replace the standalone product gate in PRODUCT_BRIEF.md.

Do not compare synthetic mechanism checks to real debugging success. The
8 public-repository tasks, 4 negative tasks, headless debugger comparisons,
and independent brand-neutral agent selection remain required for a claim
of standalone advantage. Any partial evaluation must list what was not run.

The user authorized development and appropriate GitHub/X publication on
2026-09-08. Public wording must distinguish an experimental integration from
an accepted independent product and from measured agent adoption.

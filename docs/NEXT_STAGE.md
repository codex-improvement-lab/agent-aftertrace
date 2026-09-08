# Product decision and next-stage acceptance

2026-09-08: publish a bounded VizTracer query integration for experimentation.
Do not build a competing recorder. The independent product gate remains
**NOT PASSED**.

The preflight answered an important question: existing VizTracer capture
plus a small script already recovers the fact used to motivate Aftertrace.
Making that workflow easier to invoke is a hypothesis worth testing; it is
not itself evidence of differentiation.

## Next experiment

Recruit reproducible historical debugging tasks from at least three public
repositories. Freeze eight eligible tasks in at least two failure families
and four negative tasks before running agents. The eight library compatibility
checks in this repository are ineligible as substitutes for those tasks.

Record exact source revisions, environment, user-visible symptoms, allowed
commands, capture scope, independent answer checker, and setup requirements.
Separate exploratory task development from a held-out evaluation. Keep
answer files outside agent-visible task inputs.

Compare competent workflows:

1. Plain source inspection plus pytest locals/PDB.
2. Headless mcp-debugger with ordinary documentation and helper support.
3. VizTracer plus the same reusable query support available here.
4. VizTracer plus Aftertrace and its short Skill.
5. Birdseye where its supported execution and UI route is applicable.

Count installation/setup cost, target runs, source edits, tool round trips,
recording/query overhead, disk use, total task time and answer correctness.
Count actual model usage when available. Never estimate saved tokens from
trace bytes. Permit tools to be skipped on negative tasks.

## Proposed thresholds, to freeze with the task set

- Correctness no worse than the best eligible baseline on the same tasks.
- At least 20% lower median end-to-end cost in two failure families, including
  setup and recording; report paired per-task results, not only the aggregate.
- At least 6/8 appropriate selections when the tool is available without a
  brand-specific instruction, and at most 1/4 activations on negative tasks.
- Repeat with a second agent configuration before any adoption claim.

These are proposed decision thresholds, not a preregistration of an already
completed trial. A small study remains exploratory, not population evidence.
Known-tools selection, cold discovery, first installation, repeat use and
public attention are different outcomes.

If query scripts match or beat Aftertrace, maintain a small integration or
contribute the useful pieces upstream. If full-task overhead erases the
benefit, stop expansion. Do not add dashboards, hosted storage or a broad
debugger platform to disguise that result.

## Public distribution

Publish code, reproducible checks, limits and the experimental wheel.
Use a concrete demo and solicit one difficult, reproducible debugging case.
Do not claim agent preference, time saved, real users, or a benchmark win.
Do not auto-upload recordings. Do not install the Skill into unrelated
projects or update account-wide agent configuration.

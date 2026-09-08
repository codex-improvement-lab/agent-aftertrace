# Aftertrace research and prototype guide

## Purpose

Build for coding agents that need to query captured Python execution history after a run ends. The user requires a clear reason to choose this tool, not merely JSON formatting or a new name.

## Current stage

This is an experimental, read-only VizTracer query integration. The synthetic preflight disproved the need for a new recording engine for the demonstrated fact. The package is an integration preview, not a standalone debugger accepted by M0. Agent benefit and appropriate autonomous selection remain unmeasured.

## First acceptance gate

- Compare the full workflow against pytest locals/PDB, mcp-debugger, and VizTracer with a reasonable reusable query script; include Birdseye where appropriate.
- Freeze tasks, captured information, ground-truth checks and cost criteria before measuring.
- Continue as a standalone product only if correct agents obtain a meaningful whole-task benefit and choose it appropriately without brand-specific prompting.
- If existing tracing plus a short script is equally effective and cheaper, prefer integration or upstream contribution. Do not manufacture a positive result to justify this repository.

## Scope and evidence

- Keep the preview a bounded offline reader. VizTracer owns recording; do not introduce a new tracing engine without revisiting the product gate.
- Preserve target source bytes. Restrict capture to user-selected scope and explicit size/retention limits.
- Queries inspect saved data; they must not evaluate arbitrary Python expressions or invent uncaptured values.
- First observed predicate match, prior executed line and root cause are different claims. Do not conflate them.
- Missing, truncated, sampled and unsupported data must remain visible.
- Local history may be sensitive. No automatic upload, hidden telemetry, or claim that filtering guarantees removal of all secrets.
- This project has no required dependency on Proofline, Intake, Workprint or their schemas.

## Workspace ownership

Work only in this child repository unless separately assigned. Other agents and the user may be working in sibling repositories; do not revert their edits. Run Git and project commands here. Do not create a parent Git repository.

Lab product direction and public release acceptance remain with the product-owner task. Do not move old tags, publish packages, or create remote releases from a research result alone.

On 2026-09-08 the user authorized the product owner to advance this project and perform appropriate GitHub/X actions. A tested, clearly labeled integration preview may be published; this does not waive M0 for claims of standalone advantage or agent adoption.

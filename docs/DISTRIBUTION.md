# Human discovery, agent use

Aftertrace's runtime interface serves coding agents. People still discover
the repository, decide whether to install it, and recommend it to a team.
Our distribution should make that human decision easy to assess.

## The first story

Lead with a visible debugging problem: a value can recover before a later
failure, so the final state omits part of the story. Show the small
71 / -33 example, the query, and what the result means. Put a runnable demo
beside the image. Explain the bounded JSON interface after the reader has
seen the use case.

The current card shows a synthetic example reproduced with the released
wheel. It demonstrates a capability, not saved time or a historical bug.
Credit VizTracer wherever the example is presented.

## Relevant audiences and invitations

| Audience | A useful contribution | One next step |
| --- | --- | --- |
| Python developers investigating earlier values | A runnable example and a precise explanation of what must have been recorded | Try the README demo |
| Developers reporting repetitive agent debugging | Ask which step repeats and whether a small public reproduction exists | Share a case in issue #1 |
| Tracing and debugger maintainers | Describe the integration, actual data assumptions, and a question they can answer | Review the query contract or suggest an existing API |
| Agent-tool builders | JSON examples, exit codes, bounded results, and explicit skip conditions | Try the optional query Skill on an existing trace |

Use a project's designated Show and tell space for an integration
introduction. Replies should address the actual discussion, identify our
relationship to Aftertrace, and add a useful observation or question.
Stars and likes express appreciation for the source work; they are not
evidence of anyone adopting Aftertrace.

## What earns the next larger announcement

A real debugging case is more informative than another announcement of
the same feature. Publish a case study only with a public or approved
reproduction, the baseline, capture/setup cost, the useful observation,
the verified outcome, and any additional maintenance cost. A case where
ordinary inspection wins is also useful for explaining when to skip
Aftertrace. Comparisons must follow the [next-stage gate](NEXT_STAGE.md).

Track the stages separately: exposure, a substantive reply, a reproducible
case, completed use, and voluntary repeat use. GitHub stars, X views,
self-generated clicks, and likes do not substitute for the later stages.
Until task comparisons exist, avoid numerical time/token savings claims.

This is a distribution hypothesis. The first outreach receipt records
actions performed, not a proven growth strategy. No automated recurring
posting or monitoring is enabled by this document.

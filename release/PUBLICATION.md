# Publication: Aftertrace 0.1.0a1

Published 2026-09-08T11:00:25Z as a GitHub prerelease.

[Release](https://github.com/codex-improvement-lab/agent-aftertrace/releases/tag/v0.1.0a1) · [Source-bound CI](https://github.com/codex-improvement-lab/agent-aftertrace/actions/runs/34218163483) · [Case collection](https://github.com/codex-improvement-lab/agent-aftertrace/issues/1)

- Source commit: 3b2eb81a11914fd088a4f313184f533555ebb7e5
- Tag: v0.1.0a1
- GitHub release ID: 384655084
- Maintainer account: eliasruntime; repository: codex-improvement-lab/agent-aftertrace.
- Scope: experimental, read-only VizTracer query integration.
- Independent product gate: NOT PASSED. Actual agent trials and whole-task comparisons: 0.

## Validation

50 query contract and CLI tests passed locally on Windows/Python 3.11.9.
Eight pinned library compatibility checks returned the same observed streams
as an independent query script. The first 7/8 oracle result and corrected
8/8 result remain separately recorded.

All six source-bound CI jobs passed: Ubuntu, Windows and hosted macOS on
Python 3.11 and 3.13. Each job included the contract tests, synthetic baseline
preflight, package build and installation outside the checkout.

The local published wheel also passed installation into a fresh environment,
including both module and console entry points. Its source files were checked
byte-for-byte against the tagged Git source. Source archive contents exclude
private recordings, environments and publication helpers. Frozen evidence
JSON is stored without Git newline conversion to preserve its byte hashes.

## Published assets

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| agent_aftertrace-0.1.0a1-py3-none-any.whl | 11649 | 44d5065fe3ccea176f1a63de511ca873c46f82277d7d402312ce68af4f698475 |
| agent_aftertrace-0.1.0a1.tar.gz | 38085 | 286d4a7d944db001cf57f2a968fae275aafa19d4215d427925ea2d09434dcefb |
| SHA256SUMS.txt | 206 | d2c59ec2bffc5997a8bf37d610a5b5bdbb6d26dc82ab447f4bc2d650f3fe65e3 |

All three assets were downloaded anonymously from their live release URLs
after publication, and both size and SHA-256 matched. No PyPI upload was made;
the wheel is distributed through GitHub Releases.

## Product acceptance

The [X introduction and example reply](X_PUBLICATION_2026-09-08.md) were published under @eliasruntime and verified in the browser on 2026-09-08. They link the repository and its public case-collection issue; no engagement result is claimed.

This publication establishes an available experimental integration. It does
not establish reduced debugging cost, autonomous discovery or agent preference.
The planned eight eligible debugging tasks, four negative tasks and competent
PDB/mcp-debugger/Birdseye comparisons remain outstanding. See docs/NEXT_STAGE.md.

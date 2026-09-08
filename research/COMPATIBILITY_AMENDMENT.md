# Compatibility oracle correction, 2026-09-08

The original frozen packaging check expected '2.2' and '2.2.*'.
The actual packaging 25.0 implementation retains an explicit epoch in these
intermediate strings: '0!2.2' and '0!2.2.*'.

Both the independent JSON baseline and Aftertrace returned the same four
observations. The target's public behavior assertion passed, and source
hashes stayed unchanged. The first round therefore has **7/8 expected-value
checks and 8/8 identical-stream checks**. It is retained, not relabeled as a
first-round pass, in docs/evidence/compatibility-v1*.json.

Only the packaging oracle changes in v2. The remaining seven oracles are
unchanged. The v2 manifest is frozen separately before re-running. This is
ordinary compatibility-test correction, not a new blind benchmark or a
performance result. Actual agent trials remain zero.

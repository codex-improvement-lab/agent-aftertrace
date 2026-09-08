# Aftertrace demo card

`aftertrace-demo.svg` is the editable vector card; `aftertrace-demo.png` is
the matching 1600 x 900 social/README image. The card uses no external assets.

The values were checked on 2026-09-08 using the published `0.1.0a1` wheel
and VizTracer 1.1.1 against [late_failure.py](../../research/late_failure.py).
The [README](../../README.md#try-the-complete-loop) has the recording command.
The recording intentionally ends with `AssertionError`.

Two queries against the same saved recording verified the displayed values:

```sh
aftertrace first result.json --var balance --op lt --value 0
aftertrace history result.json --var balance --offset 100 --limit 10
```

The first query returned `status: found`, `match.scalarValue: -33`, and
`rootCauseEstablished: false`. The last observation in the second query
was 71. The card labels the response as selected fields; it is an editorial
illustration of real output, not a terminal screenshot or a full response.

Recorded trace SHA-256 for this rendering:
`c5cd56a3aec928332357e31acb1600209af220a0fe9cba9179532fe227259e95`.
Trace IDs change between runs. The local synthetic recording is not part
of the distribution and the image does not include local paths or source.

This is a synthetic demonstration. It does not measure agent time saved,
tool preference, root-cause accuracy, or real-user adoption.

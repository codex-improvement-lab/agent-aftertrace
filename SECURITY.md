# Reporting problems

Use GitHub's private vulnerability reporting for a reproducible security
issue. For ordinary bugs, open an issue with a minimal synthetic recording,
expected result, command and producer version. Do not attach private traces.

This alpha reads bounded local JSON without executing expressions, importing
target code, following embedded file paths, writing files or using a network.
It is not a sandbox for running programs. The separate recorder may execute
target code and object repr methods; its limits and permissions still apply.

Supported compatibility target: VizTracer 1.1.1 and Python 3.11+.

---
name: Bug report
about: Report a reproducible problem with retrieval, generation, or documentation
title: ""
labels: ""
assignees: ""
---

<!-- For vulnerabilities, follow SECURITY.md instead of opening a public issue.
Remove API keys, private corpus content, and sensitive queries from all examples. -->

## Problem

Describe the problem and its impact.

## Steps to reproduce

1. Installation/setup:
2. Exact command (sanitized):
3. Minimal synthetic corpus, if needed:

## Expected behavior

What should happen?

## Actual behavior

Include sanitized JSON output or a traceback in a fenced code block.

## Environment

- Operating system and shell:
- Python version (`python --version`):
- Package version or commit:
- Mode (`mock` or `claude`):
- For Claude only: model and installed Anthropic SDK version:

## Retrieval context, if relevant

- `--top-k`, `--min-score`, and whether `--include-stale` was used:
- Date/time of the run and corpus freshness metadata:
- Does the problem reproduce in mock mode?

## Additional context

Related issues, workarounds, or other details.

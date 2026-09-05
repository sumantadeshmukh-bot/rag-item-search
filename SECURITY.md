# Security

## Reporting a vulnerability

Do not disclose vulnerabilities, credentials, or private corpus content in public
issues or pull requests.

If this repository is hosted on GitHub and private vulnerability reporting is
enabled, use **Security → Advisories → Report a vulnerability**. Otherwise, use a
private contact channel explicitly published by the repository owner. This source
tree does not specify a security email address or confirm that private reporting
is enabled. If neither route exists, ask the owner to enable private reporting
without including vulnerability details.

Include the affected commit or version, impact, minimal reproduction steps,
environment, and a proposed mitigation if known. Use synthetic data and redact
credentials. Coordinate disclosure with the owner before posting technical details.
No response-time or fix-time commitment is currently specified.

## Version scope

The current package baseline is `0.1.0`. No formal security support window or
backport policy has been established. When reporting, identify the exact commit
and whether the issue reproduces on the current source tree.

## Data handling and boundaries

- Mock mode performs local retrieval without calling a model service.
- Claude mode sends the query and retrieved source IDs, titles, and full chunk
  text to Anthropic. Only use corpus content you are authorized to send there.
- CLI output contains the original query and full retrieved text. Treat saved
  output, terminal history, logs, and issue attachments accordingly.
- `ANTHROPIC_API_KEY` is read from the environment. The application does not
  intentionally print or persist it, and `.env` is ignored by Git, but this is
  not a guarantee against secrets leaking through other tools or diagnostics.
- Corpus text is included in the model prompt. Grounding instructions and
  citations are not a defense against prompt injection or incorrect answers.
- Freshness metadata is supplied by the corpus author; it does not authenticate
  sources or prove accuracy. `--include-stale` bypasses stale-entry exclusion.
- Corpus validation is limited. This example has no authentication, per-user
  authorization, sandbox for untrusted inputs, or production service hardening.

Keep secrets out of the corpus and committed files. If a credential is exposed,
revoke or rotate it with its provider; deleting a visible copy alone is insufficient.

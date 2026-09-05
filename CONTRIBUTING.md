# Contributing

Keep changes focused on this project's purpose: a small, understandable RAG
example with observable context, explicit freshness handling, and a keyless mock
mode. Bug fixes, documentation improvements, and focused examples are welcome.

## Development setup

Use Python 3.11 or newer. From your checkout on Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Only install `python -m pip install -e ".[claude]"` when working on the optional
Claude integration. Set credentials in your environment; `.env.example` is a
reference and `.env` is not loaded automatically. Never commit real credentials.

## Making a change

1. For a substantial behavior change, open a feature request describing the
   problem and proposed scope. Small fixes can go straight to a pull request.
2. Create a focused branch in your checkout or fork.
3. Follow the existing Python style, type hints, and separation between corpus
   loading, retrieval, generation, and CLI output. Avoid unnecessary dependencies.
4. Add or adjust tests for behavior changes. Use deterministic fixtures and mock
   generation; ordinary tests must not need API keys or network access. Pass an
   explicit `now` when testing freshness through `TfidfIndex.search`.
5. Update relevant documentation and add user-visible changes under
   `Unreleased` in [CHANGELOG.md](CHANGELOG.md).
6. Open a pull request using the repository template. Explain the problem,
   resulting behavior, and checks performed; link related issues if available.

## Validation

With the virtual environment active:

```powershell
python -m unittest discover -s tests -v
rag-item-search --help
rag-item-search "How long does standard shipping take?"
rag-item-search "How do I grow tomatoes?"
git diff --check
```

The suite covers ranking, stale exclusion, no-match behavior, and end-to-end
context visibility. The end-to-end tests use the bundled corpus and wall-clock
freshness, so inspect the dates if those tests begin failing after entries expire.
Do not change source dates just to suppress a failure. There is no configured
formatter, linter, or CI workflow in this repository at present.

For documentation-only changes, check examples against the implementation and
verify relative links and formatting. Report checks you could not run and why.
Live Claude checks are optional, require your own credentials, and may cost money;
sanitize any output shared in reviews.

## Issues and security

Use the bug-report template for reproduction steps, expected/actual behavior,
Python version, and sanitized output. Use the feature-request template for a
concrete use case and alternatives. Keep comments respectful and actionable.

Do not post vulnerabilities or secrets in public issues. Follow
[SECURITY.md](SECURITY.md) for private reporting guidance. The repository currently
has no license file or contributor license agreement; do not assume an unstated
license applies.

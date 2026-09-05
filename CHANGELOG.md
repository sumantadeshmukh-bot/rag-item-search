# Changelog

User-visible changes are recorded here. Package versions are defined in
`pyproject.toml`; this file does not imply that a version has been published.

## Unreleased

### Added

- Contribution and security guidance.
- GitHub bug-report, feature-request, and pull-request templates.
- CLI subprocess tests for top-k truncation and relevance-threshold filtering.

### Changed

- Updated the default Claude model to `claude-sonnet-5` in code and configuration
  examples, removed its unsupported temperature override, and documented periodic
  model checks.
- Expanded README setup instructions, CLI reference, output documentation,
  corpus format, troubleshooting, and project limitations.

## 0.1.0 — Initial repository baseline

This is the version in the initial source tree; no release date is recorded.

### Added

- Local JSON FAQ corpus with per-entry freshness metadata.
- In-memory TF-IDF retrieval with cosine ranking, a relevance threshold,
  top-k selection, and stale-entry exclusion.
- CLI JSON output exposing retrieved chunks and stale exclusions.
- Deterministic mock generation and optional Anthropic Claude generation.
- Retrieval and end-to-end tests using Python's `unittest`.

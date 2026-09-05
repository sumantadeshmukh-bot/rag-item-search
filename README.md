# rag-item-search

A deliberately small, working Retrieval-Augmented Generation (RAG) example. It
retrieves current FAQ entries from a local corpus, visibly returns the exact
retrieved chunks, and optionally asks Claude to produce a grounded answer.

## Why this design

- **Python and an in-memory TF-IDF index:** the retrieval algorithm stays visible
  and needs no database, model download, or embedding service.
- **Cosine similarity with a threshold:** `top-k` alone always returns something;
  the threshold enables an honest no-match outcome.
- **Explicit freshness metadata:** each item has `updated_at` and `max_age_days`.
  Stale matches are excluded by default and listed under `stale_exclusions`.
- **Transparent output:** `retrieved_context` contains full chunk text, source ID,
  title, score, and timestamp. Context is observable, not hidden behind citations.
- **Two generation modes:** deterministic mock mode makes local tests and CI
  reliable; Claude mode exercises the real Anthropic Messages API.

This example treats each short FAQ entry as one chunk. For larger documents, a
production ingestion step would split text into overlapping passages before
building the same index.

## Project layout

```text
data/items.json                 local corpus and freshness metadata
src/rag_item_search/corpus.py   loading and stale-data rules
src/rag_item_search/retrieval.py TF-IDF vectors and cosine ranking
src/rag_item_search/generation.py mock and Claude generators
src/rag_item_search/cli.py      end-to-end CLI and transparent JSON output
tests/                          retrieval and end-to-end tests
```

## Run without an API key

Requires **Python 3.11 or newer** and pip. Run these commands from a local
checkout of this repository. Mock mode has no runtime dependencies or API calls.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
rag-item-search "How long does standard shipping take?"
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
rag-item-search "How long does standard shipping take?"
```

The default `mock` mode performs real retrieval but uses a deterministic answer.
The JSON response visibly includes `retrieved_context`, `stale_exclusions`, and
`answer`.

## Run with Claude

Install the optional Anthropic SDK and set your key in the environment:

```powershell
python -m pip install -e ".[claude]"
$env:ANTHROPIC_API_KEY = "your-key"
rag-item-search "How long does standard shipping take?" --mode claude
```

Optionally set `CLAUDE_MODEL` or pass `--model`. The default is
`claude-sonnet-4-20250514`. The API key is read only from the environment and is
never written or printed by this project.

On macOS/Linux, set the key with `export ANTHROPIC_API_KEY="your-key"`.
[.env.example](.env.example) lists the environment variables for reference;
the application does **not** automatically load `.env` files. Model selection
uses `--model`, then `CLAUDE_MODEL`, then the code default above. Choose a model
available to your Anthropic account.

Claude mode sends the query and retrieved titles, IDs, and full text to Anthropic
and may incur API charges. When no chunks qualify, generation is skipped in both
modes. See [SECURITY.md](SECURITY.md) for data-handling limitations.

## CLI reference

```text
rag-item-search QUERY [--mode {mock,claude}] [--model MODEL]
                      [--corpus PATH] [--top-k N] [--min-score SCORE]
                      [--include-stale]
```

| Argument | Default | Behavior |
| --- | --- | --- |
| `QUERY` | Required | Question to retrieve context for; quote multiword queries. |
| `--mode` | `mock` | Deterministic mock answer or Claude generation. |
| `--model` | Environment/code default | Model override for Claude mode. |
| `--corpus` | Checkout's `data/items.json` | Path to a UTF-8 JSON corpus. |
| `--top-k` | `3` | Maximum returned chunks; must be at least 1. |
| `--min-score` | `0.12` | Minimum cosine similarity; normally use a value between 0 and 1. |
| `--include-stale` | Disabled | Allow stale chunks into retrieved context. |
| `--help` | — | Show command help. |

The module entry point is also available as `python -m rag_item_search.cli`.
Use an editable install as shown above for the bundled corpus; when distributing
an installation separately from the checkout, supply `--corpus` explicitly.

## Output

Successful runs print JSON to standard output:

- `query`: the original question.
- `retrieved_context`: ranked chunks with `id`, `title`, `score` (rounded to four
  decimals), `updated_at`, and full `text`.
- `stale_exclusions`: matching stale entries with `id`, `title`, `updated_at`,
  and `max_age_days`; this is not a list of every stale entry in the corpus.
- `answer`: a deterministic source-reference message in mock mode, a model
  response in Claude mode, or a no-match message.

A no-match result is successful output with an empty `retrieved_context`, not an
error. Scores measure lexical similarity, not the probability an answer is correct.

## Retrieval strategies to try

```powershell
# More or fewer candidates
rag-item-search "Tell me about delivery" --top-k 1

# Stricter relevance filtering
rag-item-search "Tell me about delivery" --min-score 0.25

# Demonstrate an honest no-match
rag-item-search "How do I grow tomatoes?"
```

`top-k` limits breadth while `--min-score` controls confidence. Increasing the
threshold reduces weak context and increases no-match responses. In larger
systems, useful next steps would be semantic embeddings, hybrid lexical/vector
retrieval, metadata filters, and reranking.

## Stale-data handling

At query time, matching entries older than their `max_age_days` are omitted and
reported in `stale_exclusions`. This prevents an old but lexically strong result
from silently grounding an answer. Corpus updates take effect on the next CLI run
because the small index is rebuilt from `data/items.json` each time.

For diagnosis only, `--include-stale` allows stale chunks to participate. A real
system would normally refresh the source or fail closed rather than enable this.

## Test

```powershell
python -m unittest discover -s tests -v
```

Tests cover relevance ranking, threshold-based no-match behavior, stale exclusion,
and full retrieved-context visibility in the end-to-end mock output.

## Use your own corpus

Create a UTF-8 JSON array with one short entry per chunk:

```json
[
  {
    "id": "shipping",
    "title": "Standard shipping",
    "text": "Standard shipping takes three to five business days.",
    "updated_at": "2026-08-20T00:00:00Z",
    "max_age_days": 365
  }
]
```

All five fields are required. Use unique string IDs, string titles and text,
ISO 8601 timestamps with a timezone, and nonnegative integer freshness limits.
The loader treats timestamps without a timezone as UTC and performs only limited
validation. Set `updated_at` to when the source was actually verified or updated.

```powershell
rag-item-search "How long does shipping take?" --corpus data/items.json
```

Freshness uses the current UTC time: an entry is stale when its age is strictly
greater than `max_age_days`. The bundled examples eventually expire, so results
can change with the date. The index includes all entries when computing TF-IDF;
stale filtering happens during search, before selecting the top results.

## Troubleshooting and limitations

- **Command not found:** activate the virtual environment and install with
  `python -m pip install -e .`, or use the module entry point above.
- **Missing Claude dependency/key:** install `.[claude]` and set
  `ANTHROPIC_API_KEY` in the same shell that runs the command.
- **No current matches:** inspect `stale_exclusions`, check source timestamps,
  and try wording that shares terms with the corpus. Use `--include-stale` only
  to diagnose freshness filtering.
- **Corpus loading errors:** check the path, JSON syntax, required fields, and
  timestamp formats. Malformed records may raise an exception.

This is a learning example, with English-oriented lexical tokenization, one
chunk per entry, and an index rebuilt on every run. It has no semantic embeddings,
automatic source refresh, access controls, or guarantee that model answers are
correct. Tests use mock mode and do not verify live API availability; end-to-end
tests also depend on the bundled corpus remaining fresh.

## Project documentation

- [Contributing](CONTRIBUTING.md): development setup, checks, and review workflow.
- [Changelog](CHANGELOG.md): recorded changes and the current package baseline.
- [Security](SECURITY.md): reporting guidance and data-handling boundaries.
- [Bug report](.github/ISSUE_TEMPLATE/bug_report.md) and
  [feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates.

No license file is currently included in this repository.

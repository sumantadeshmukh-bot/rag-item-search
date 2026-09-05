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

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
rag-item-search "How long does standard shipping take?"
```

The default `mock` mode performs real retrieval but uses a deterministic answer.
The JSON response visibly includes `retrieved_context`, `stale_exclusions`, and
`answer`.

## Run with Claude

Install the optional Anthropic SDK and set your key in the environment:

```powershell
pip install -e ".[claude]"
$env:ANTHROPIC_API_KEY = "your-key"
rag-item-search "How long does standard shipping take?" --mode claude
```

Optionally set `CLAUDE_MODEL` or pass `--model`. The default is
`claude-sonnet-4-20250514`. The API key is read only from the environment and is
never written or printed by this project.

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

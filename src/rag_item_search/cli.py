from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .corpus import load_documents
from .generation import ClaudeGenerator, MockGenerator
from .retrieval import SearchResult, TfidfIndex

DEFAULT_CORPUS = Path(__file__).resolve().parents[2] / "data" / "items.json"


def build_output(query: str, result: SearchResult, answer: str) -> dict[str, object]:
    return {
        "query": query,
        "retrieved_context": [
            {
                "id": hit.document.id,
                "title": hit.document.title,
                "score": round(hit.score, 4),
                "updated_at": hit.document.updated_at.isoformat(),
                "text": hit.document.text,
            }
            for hit in result.hits
        ],
        "stale_exclusions": [
            {
                "id": document.id,
                "title": document.title,
                "updated_at": document.updated_at.isoformat(),
                "max_age_days": document.max_age_days,
            }
            for document in result.stale_exclusions
        ],
        "answer": answer,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    documents = load_documents(args.corpus)
    result = TfidfIndex(documents).search(
        args.query,
        top_k=args.top_k,
        min_score=args.min_score,
        include_stale=args.include_stale,
    )

    if not result.hits:
        answer = "I could not find sufficiently relevant, current information in the local corpus."
        return build_output(args.query, result, answer)

    if args.mode == "claude":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is required for --mode claude")
        generator = ClaudeGenerator(model=args.model)
    else:
        generator = MockGenerator()
    return build_output(args.query, result, generator.answer(args.query, result.hits))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Transparent RAG item search")
    result.add_argument("query", help="Question to answer from the local corpus")
    result.add_argument("--mode", choices=("mock", "claude"), default="mock")
    result.add_argument("--model", help="Claude model override")
    result.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    result.add_argument("--top-k", type=int, default=3)
    result.add_argument("--min-score", type=float, default=0.12)
    result.add_argument("--include-stale", action="store_true")
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        output = run(args)
    except (OSError, ValueError, RuntimeError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


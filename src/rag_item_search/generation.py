from __future__ import annotations

import os
from typing import Protocol

from .retrieval import SearchHit


class Generator(Protocol):
    def answer(self, query: str, hits: list[SearchHit]) -> str: ...


def format_context(hits: list[SearchHit]) -> str:
    return "\n\n".join(
        f"[{hit.document.id}] {hit.document.title}\n{hit.document.text}"
        for hit in hits
    )


class MockGenerator:
    """Deterministic generator for tests and keyless demonstrations."""

    def answer(self, query: str, hits: list[SearchHit]) -> str:
        sources = ", ".join(f"[{hit.document.id}]" for hit in hits)
        return f"Mock grounded answer for '{query}'. Consult {sources}."


class ClaudeGenerator:
    def __init__(self, model: str | None = None):
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Claude mode requires the optional dependency: pip install -e '.[claude]'"
            ) from exc
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model or os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

    def answer(self, query: str, hits: list[SearchHit]) -> str:
        context = format_context(hits)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=(
                "Answer only from the supplied context. Cite factual statements with the "
                "source ID in square brackets. If context is insufficient, say so plainly."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nRetrieved context:\n{context}",
                }
            ],
        )
        return "".join(block.text for block in message.content if block.type == "text")

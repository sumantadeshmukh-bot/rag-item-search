from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone

from .corpus import Document

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "of", "on", "or", "should", "the",
    "to", "what", "when", "where", "which", "who", "why", "with",
}


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOP_WORDS]


@dataclass(frozen=True)
class SearchHit:
    document: Document
    score: float


@dataclass(frozen=True)
class SearchResult:
    hits: list[SearchHit]
    stale_exclusions: list[Document]


class TfidfIndex:
    """A tiny immutable TF-IDF index suitable for a small learning corpus."""

    def __init__(self, documents: list[Document]):
        self.documents = documents
        token_sets = [set(tokenize(f"{doc.title} {doc.text}")) for doc in documents]
        document_frequency = Counter(token for tokens in token_sets for token in tokens)
        count = max(len(documents), 1)
        self.idf = {
            token: math.log((1 + count) / (1 + frequency)) + 1
            for token, frequency in document_frequency.items()
        }
        self.vectors = [self._vectorize(f"{doc.title} {doc.text}") for doc in documents]

    def _vectorize(self, text: str) -> dict[str, float]:
        counts = Counter(tokenize(text))
        total = sum(counts.values()) or 1
        return {
            token: (frequency / total) * self.idf.get(token, 0.0)
            for token, frequency in counts.items()
            if token in self.idf
        }

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        dot = sum(value * right.get(token, 0.0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0

    def search(
        self,
        query: str,
        *,
        top_k: int = 3,
        min_score: float = 0.12,
        now: datetime | None = None,
        include_stale: bool = False,
    ) -> SearchResult:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        now = now or datetime.now(timezone.utc)
        query_vector = self._vectorize(query)
        candidates: list[SearchHit] = []
        stale: list[Document] = []

        for document, vector in zip(self.documents, self.vectors, strict=True):
            score = self._cosine(query_vector, vector)
            if score < min_score:
                continue
            if document.is_stale(now) and not include_stale:
                stale.append(document)
                continue
            candidates.append(SearchHit(document=document, score=score))

        candidates.sort(key=lambda hit: (-hit.score, hit.document.id))
        return SearchResult(hits=candidates[:top_k], stale_exclusions=stale)

from datetime import datetime, timezone
import unittest

from rag_item_search.corpus import Document
from rag_item_search.retrieval import TfidfIndex

NOW = datetime(2026, 9, 5, tzinfo=timezone.utc)


def document(identifier: str, text: str, updated: datetime, max_age: int = 365) -> Document:
    return Document(identifier, identifier.title(), text, updated, max_age)


class RetrievalTests(unittest.TestCase):
    def test_retrieval_ranks_relevant_document_first(self):
        docs = [
            document("shipping", "Standard shipping takes five days", NOW),
            document("returns", "Returns receive a refund", NOW),
        ]
        result = TfidfIndex(docs).search(
            "How long does shipping take?", now=NOW, min_score=0.01
        )
        self.assertEqual(result.hits[0].document.id, "shipping")

    def test_stale_relevant_document_is_excluded_and_reported(self):
        old = datetime(2020, 1, 1, tzinfo=timezone.utc)
        docs = [document("legacy", "same-day shipping promotion", old, max_age=30)]
        result = TfidfIndex(docs).search("shipping promotion", now=NOW, min_score=0.01)
        self.assertEqual(result.hits, [])
        self.assertEqual([doc.id for doc in result.stale_exclusions], ["legacy"])

    def test_unrelated_query_returns_no_hits(self):
        docs = [document("shipping", "Standard shipping takes five days", NOW)]
        result = TfidfIndex(docs).search("How do I grow tomatoes?", now=NOW)
        self.assertEqual(result.hits, [])


if __name__ == "__main__":
    unittest.main()

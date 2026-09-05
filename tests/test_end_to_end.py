from argparse import Namespace
from pathlib import Path
import unittest

from rag_item_search.cli import run

CORPUS = Path(__file__).parents[1] / "data" / "items.json"


def arguments(query: str) -> Namespace:
    return Namespace(
        query=query,
        mode="mock",
        model=None,
        corpus=CORPUS,
        top_k=2,
        min_score=0.12,
        include_stale=False,
    )


class EndToEndTests(unittest.TestCase):
    def test_mock_path_exposes_full_retrieved_context(self):
        output = run(arguments("How long does standard shipping take?"))
        self.assertTrue(output["retrieved_context"])
        self.assertTrue(output["retrieved_context"][0]["text"])
        self.assertEqual(output["retrieved_context"][0]["id"], "shipping")
        self.assertIn("Mock grounded answer", output["answer"])

    def test_no_match_is_graceful_and_skips_generation(self):
        output = run(arguments("What soil should I use for orchids?"))
        self.assertEqual(output["retrieved_context"], [])
        self.assertIn("could not find", output["answer"])


if __name__ == "__main__":
    unittest.main()

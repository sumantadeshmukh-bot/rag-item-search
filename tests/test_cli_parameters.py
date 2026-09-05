from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliParameterTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.corpus = Path(temporary.name) / "items.json"
        # Fresh synthetic data keeps these tests independent of bundled FAQ expiry.
        timestamp = datetime.now(timezone.utc).isoformat()
        self.corpus.write_text(json.dumps([
            {
                "id": identifier,
                "title": title,
                "text": text,
                "updated_at": timestamp,
                "max_age_days": 1,
            }
            for identifier, title, text in [
                ("standard", "Standard shipping", "Shipping takes five days"),
                ("express", "Express shipping", "Shipping takes two days"),
            ]
        ]), encoding="utf-8")

    def cli(self, *options):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [sys.executable, "-m", "rag_item_search.cli", "shipping",
             "--mode", "mock", "--corpus", str(self.corpus), *options],
            cwd=ROOT, env=environment, capture_output=True, text=True,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_top_k_one_truncates_matching_results(self):
        broad = self.cli("--top-k", "3", "--min-score", "0.1")
        limited = self.cli("--top-k", "1", "--min-score", "0.1")
        self.assertEqual(len(broad["retrieved_context"]), 2)
        self.assertEqual(limited["retrieved_context"], broad["retrieved_context"][:1])

    def test_stricter_min_score_excludes_low_threshold_matches(self):
        permissive = self.cli("--min-score", "0.1")
        strict = self.cli("--min-score", "0.9")
        self.assertEqual(len(permissive["retrieved_context"]), 2)
        for hit in permissive["retrieved_context"]:
            self.assertGreaterEqual(hit["score"], 0.1)
            self.assertLess(hit["score"], 0.9)
        self.assertEqual(strict["retrieved_context"], [])
        self.assertEqual(strict["stale_exclusions"], [])
        self.assertIn("could not find", strict["answer"])


if __name__ == "__main__":
    unittest.main()

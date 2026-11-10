from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mobdeen_guardian.kb import KnowledgeBase  # noqa: E402


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "ingestion" / "build_index.py")], cwd=ROOT, check=True)
        cls.kb = KnowledgeBase(ROOT / "data" / "index.json")

    def ids_for(self, query: str) -> set[str]:
        return {hit.source.source_id for hit in self.kb.search(query, top_k=6)}

    def test_uae_privacy_query(self):
        ids = self.ids_for("UAE child personal data privacy minimize identifiers")
        self.assertIn("UAE-PDPL", ids)

    def test_age_appropriate_query(self):
        ids = self.ids_for("age appropriate child content guardian Arabic")
        self.assertTrue({"UK-CHILDRENS-CODE", "UNICEF-AI-CHILDREN-V3"} & ids)

    def test_y3172_query(self):
        ids = self.ids_for("SRC collector preprocessor model policy distributor sink MLFO")
        self.assertIn("ITU-Y3172", ids)

    def test_commercial_vulnerability_query(self):
        ids = self.ids_for("commercial targeting inferred child vulnerability")
        self.assertIn("EU-AI-ACT", ids)


if __name__ == "__main__":
    unittest.main()


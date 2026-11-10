from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mobdeen_guardian.agent import MobdeenGuardianAgent  # noqa: E402
from mobdeen_guardian.audit import AuditLogger  # noqa: E402
from mobdeen_guardian.kb import KnowledgeBase  # noqa: E402
from mobdeen_guardian.models import AgentRequest  # noqa: E402


class ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "ingestion" / "build_index.py")], cwd=ROOT, check=True)
        cls.scenario = json.loads((ROOT / "scenarios" / "child_safety_progressive.json").read_text(encoding="utf-8"))

    def test_all_progressive_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            agent = MobdeenGuardianAgent(KnowledgeBase(ROOT / "data" / "index.json"), AuditLogger(audit_path))
            responses = []
            for step in self.scenario["steps"]:
                request = AgentRequest(
                    scenario_step=step["step"],
                    actor=step["actor"],
                    audience=step["audience"],
                    text=step["text"],
                    purpose=step["purpose"],
                    family_context=step["family_context"],
                )
                response = agent.decide(request)
                responses.append(response)
                self.assertEqual(step["expected_action"], response.action)
                self.assertEqual("PASS", response.result)
                self.assertGreaterEqual(len(response.sources), 2)

            audit_records = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(3, len(audit_records))
            self.assertTrue(all("input_fingerprint_sha256" in item for item in audit_records))
            self.assertTrue(all("raw_input" not in item for item in audit_records))
            self.assertNotIn("050 123 4567", audit_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


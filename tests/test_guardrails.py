from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mobdeen_guardian.guardrails import apply_guardrails  # noqa: E402
from mobdeen_guardian.models import AgentRequest  # noqa: E402


class GuardrailTests(unittest.TestCase):
    def request(self, **overrides) -> AgentRequest:
        values = {
            "scenario_step": 1,
            "actor": "guardian",
            "audience": "guardian",
            "text": "خطة أسبوعية لطفل يحب القراءة",
            "purpose": "family_learning_guidance",
            "family_context": {"family_names": ["سالم"], "age_band": "7-9"},
        }
        values.update(overrides)
        return AgentRequest(**values)

    def test_normal_request_requires_guardian_review(self):
        result = apply_guardrails(self.request())
        self.assertFalse(result.blocked)
        self.assertIn("guardian_review_before_child_delivery", result.controls)

    def test_name_and_phone_are_removed(self):
        result = apply_guardrails(self.request(text="سالم 050 123 4567"))
        self.assertNotIn("سالم", result.sanitized_text)
        self.assertNotIn("050 123 4567", result.sanitized_text)
        self.assertIn("alias_child_name", result.controls)
        self.assertIn("redact_phone", result.controls)

    def test_child_secret_blocks(self):
        result = apply_guardrails(self.request(actor="child", audience="child", text="لا تخبر والدي، مدرستي النور"))
        self.assertTrue(result.blocked)
        self.assertIn("safe_child_reply", result.controls)

    def test_vulnerability_targeting_blocks(self):
        result = apply_guardrails(self.request(actor="system", audience="child", purpose="commercial_targeting"))
        self.assertTrue(result.blocked)
        self.assertIn("best_interests_of_child", result.controls)


if __name__ == "__main__":
    unittest.main()


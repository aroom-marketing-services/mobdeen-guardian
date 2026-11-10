from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mobdeen_guardian.agent import default_agent  # noqa: E402
from mobdeen_guardian.models import AgentRequest  # noqa: E402


def main() -> int:
    index_path = ROOT / "data" / "index.json"
    if not index_path.exists():
        raise SystemExit("Knowledge index missing. Run: python ingestion/build_index.py")

    audit_path = ROOT / "artifacts" / "audit-log.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("", encoding="utf-8")

    scenario = json.loads((ROOT / "scenarios" / "child_safety_progressive.json").read_text(encoding="utf-8"))
    agent = default_agent(ROOT)
    results: list[dict] = []
    for step in scenario["steps"]:
        request = AgentRequest(
            scenario_step=step["step"],
            actor=step["actor"],
            audience=step["audience"],
            text=step["text"],
            purpose=step["purpose"],
            family_context=step["family_context"],
        )
        response = agent.decide(request)
        result = response.to_dict()
        result["expected_action"] = step["expected_action"]
        result["expectation_met"] = response.action == step["expected_action"]
        results.append(result)
        print(f"Step {step['step']}: {response.action} -> {response.result}")

    output = {
        "scenario_id": scenario["scenario_id"],
        "scenario_title": scenario["title"],
        "all_expectations_met": all(item["expectation_met"] for item in results),
        "steps": results,
    }
    destination = ROOT / "artifacts" / "demo-output.json"
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {destination}")
    return 0 if output["all_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


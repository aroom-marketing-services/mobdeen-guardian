from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import default_agent
from .models import AgentRequest


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Mobdeen Guardian policy-grounded agent")
    parser.add_argument("text", help="Synthetic request text")
    parser.add_argument("--actor", choices=["guardian", "child", "system"], default="guardian")
    parser.add_argument("--audience", choices=["guardian", "child"], default="guardian")
    parser.add_argument("--purpose", default="family_learning_guidance")
    parser.add_argument("--step", type=int, default=1)
    args = parser.parse_args()

    root = _project_root()
    request = AgentRequest(
        scenario_step=args.step,
        actor=args.actor,
        audience=args.audience,
        text=args.text,
        purpose=args.purpose,
        family_context={"family_names": [], "age_band": "7-9"},
    )
    response = default_agent(root).decide(request)
    print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


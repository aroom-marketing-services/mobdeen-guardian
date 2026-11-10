from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .models import AgentRequest, AgentResponse


class AuditLogger:
    """Writes reviewable records without storing raw child input."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def fingerprint(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def write(self, request: AgentRequest, response: AgentResponse) -> dict:
        record = {
            "event_id": response.event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scenario_step": request.scenario_step,
            "actor": request.actor,
            "audience": request.audience,
            "purpose": request.purpose,
            "input_fingerprint_sha256": self.fingerprint(request.text),
            "input_classification": response.classifications,
            "retrieved_sources": [
                {
                    "source_id": source.source_id,
                    "title": source.title,
                    "authority": source.authority,
                    "section": source.section,
                    "url": source.url,
                }
                for source in response.sources
            ],
            "applied_controls": response.applied_controls,
            "decision_summary": response.decision_summary,
            "action": response.action,
            "result": response.result,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record


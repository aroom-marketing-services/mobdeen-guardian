from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    title: str
    authority: str
    url: str
    section: str
    score: float


@dataclass(frozen=True)
class GuardrailResult:
    sanitized_text: str
    classifications: list[str] = field(default_factory=list)
    controls: list[str] = field(default_factory=list)
    blocked: bool = False
    reason: str = ""


@dataclass(frozen=True)
class AgentRequest:
    scenario_step: int
    actor: str
    audience: str
    text: str
    purpose: str
    family_context: dict[str, Any]


@dataclass(frozen=True)
class AgentResponse:
    event_id: str
    action: str
    decision_summary: str
    response_text: str
    classifications: list[str]
    applied_controls: list[str]
    sources: list[SourceRef]
    result: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["sources"] = [asdict(source) for source in self.sources]
        return data


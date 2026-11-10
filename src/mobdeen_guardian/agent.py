from __future__ import annotations

import uuid
from pathlib import Path

from .audit import AuditLogger
from .generator import OfflineGenerator, TextGenerator
from .guardrails import apply_guardrails, with_sanitized_text
from .kb import KnowledgeBase
from .models import AgentRequest, AgentResponse, SourceRef


SAFE_CHILD_REPLY = (
    "شكرًا لأنك أخبرتني. لن أشارك معلوماتك هنا. تحدث مع أحد والديك أو شخص بالغ تثق به "
    "إذا كان الأمر يقلقك."
)

COMMERCIAL_BLOCK_REPLY = (
    "تم إيقاف الاقتراح لأنه يستخدم استنتاجًا عن طفل لغرض تجاري. يحتاج هذا القرار إلى مراجعة "
    "بشرية مستقلة ولا يجوز عرضه للطفل."
)


class MobdeenGuardianAgent:
    def __init__(
        self,
        kb: KnowledgeBase,
        audit: AuditLogger,
        generator: TextGenerator | None = None,
    ):
        self.kb = kb
        self.audit = audit
        self.generator = generator or OfflineGenerator()

    def _retrieve(self, request: AgentRequest, classifications: list[str]) -> list[SourceRef]:
        general_query = " ".join(
            [
                request.purpose,
                request.text,
                "child privacy guardian consent age appropriate Arabic human supervision",
                " ".join(classifications),
            ]
        )
        queries = [general_query]
        if "direct_identifier" in classifications or any(item.startswith("child_") for item in classifications):
            queries.insert(0, "UAE personal data protection child privacy minimization guardian safety")
        if "commercial_targeting" in classifications:
            queries.insert(0, "EU AI Act exploit age vulnerability harmful manipulation commercial targeting")

        ordered: list[SourceRef] = []
        seen: set[tuple[str, str]] = set()
        for query in queries:
            for hit in self.kb.search(query, top_k=5):
                key = (hit.source.source_id, hit.source.section)
                if key not in seen:
                    seen.add(key)
                    ordered.append(hit.source)
                if len(ordered) == 5:
                    return ordered
        return ordered

    def decide(self, request: AgentRequest) -> AgentResponse:
        guardrail = apply_guardrails(request)
        sanitized_request = with_sanitized_text(request, guardrail)
        sources = self._retrieve(sanitized_request, guardrail.classifications)
        event_id = str(uuid.uuid4())

        if guardrail.blocked and "commercial_targeting" in guardrail.classifications:
            response = AgentResponse(
                event_id=event_id,
                action="BLOCK_AND_ESCALATE",
                decision_summary=(
                    "The proposed commercial action depends on an inferred child vulnerability. "
                    "Purpose limitation and the child's best interests require a human policy review."
                ),
                response_text=COMMERCIAL_BLOCK_REPLY,
                classifications=guardrail.classifications,
                applied_controls=guardrail.controls,
                sources=sources,
                result="PASS",
            )
        elif guardrail.blocked:
            response = AgentResponse(
                event_id=event_id,
                action="BLOCK_AND_NOTIFY_GUARDIAN",
                decision_summary=(
                    "Direct child context and a secrecy request were detected. Identifiers were removed, "
                    "the content was withheld from the provider, and guardian review was required."
                ),
                response_text=SAFE_CHILD_REPLY,
                classifications=guardrail.classifications,
                applied_controls=guardrail.controls,
                sources=sources,
                result="PASS",
            )
        else:
            source_lines = "\n".join(f"- {source.title}: {source.url}" for source in sources)
            system = (
                "You create short Arabic family-learning plans. Use only minimized context. "
                "Do not address the child directly. The supervising parent must approve every output.\n"
                + source_lines
            )
            generated = self.generator.generate(system, sanitized_request.text)
            response = AgentResponse(
                event_id=event_id,
                action="ALLOW_WITH_GUARDIAN_REVIEW",
                decision_summary=(
                    "The request uses an age band and general interests only. The result is held for "
                    "guardian approval and linked to retrieved policy sources."
                ),
                response_text=generated,
                classifications=guardrail.classifications,
                applied_controls=guardrail.controls,
                sources=sources,
                result="PASS",
            )

        self.audit.write(request, response)
        return response


def default_agent(project_root: Path) -> MobdeenGuardianAgent:
    return MobdeenGuardianAgent(
        kb=KnowledgeBase(project_root / "data" / "index.json"),
        audit=AuditLogger(project_root / "artifacts" / "audit-log.jsonl"),
    )


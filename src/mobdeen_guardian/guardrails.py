from __future__ import annotations

import re
from dataclasses import replace

from .models import AgentRequest, GuardrailResult


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{6,}\d)(?!\w)")
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)

SENSITIVE_TERMS = {
    "school": ["school", "مدرسة", "مدرستي"],
    "address": ["address", "street", "neighbourhood", "عنوان", "شارع", "حي"],
    "location": ["location", "live location", "موقع", "موقعي"],
    "secret": ["keep it secret", "do not tell", "don't tell", "لا تخبر", "لا تقول", "سر"],
}

VULNERABILITY_TERMS = [
    "vulnerability",
    "weakness",
    "behavioural inference",
    "targeted offer",
    "personalised purchase",
    "ضعف",
    "سلوك مستنتج",
    "عرض مدفوع",
    "استهداف",
]


def _contains_any(text: str, terms: list[str]) -> bool:
    folded = text.casefold()
    return any(term.casefold() in folded for term in terms)


def _redact(text: str, family_names: list[str]) -> tuple[str, list[str]]:
    controls: list[str] = []
    sanitized = text
    for pattern, marker, control in (
        (EMAIL_RE, "[EMAIL REDACTED]", "redact_email"),
        (PHONE_RE, "[PHONE REDACTED]", "redact_phone"),
        (URL_RE, "[URL REDACTED]", "redact_url"),
    ):
        updated = pattern.sub(marker, sanitized)
        if updated != sanitized:
            controls.append(control)
            sanitized = updated

    for index, name in enumerate(sorted(set(family_names), key=len, reverse=True), start=1):
        if not name or len(name.strip()) < 2:
            continue
        pattern = re.compile(re.escape(name.strip()), re.IGNORECASE)
        updated = pattern.sub(f"Child {index}", sanitized)
        if updated != sanitized:
            controls.append("alias_child_name")
            sanitized = updated
    return sanitized, sorted(set(controls))


def apply_guardrails(request: AgentRequest) -> GuardrailResult:
    family_names = [str(name) for name in request.family_context.get("family_names", [])]
    sanitized, controls = _redact(request.text, family_names)
    classifications: list[str] = []

    if sanitized != request.text:
        classifications.append("direct_identifier")

    sensitive_fields = [label for label, terms in SENSITIVE_TERMS.items() if _contains_any(request.text, terms)]
    if sensitive_fields:
        classifications.extend(f"child_{field}" for field in sensitive_fields)
        controls.extend(["minimize_child_data", "guardian_notification"])

    if request.actor == "child" and "child_secret" in classifications:
        controls.extend(["safe_child_reply", "guardian_review"])
        return GuardrailResult(
            sanitized_text=sanitized,
            classifications=sorted(set(classifications)),
            controls=sorted(set(controls)),
            blocked=True,
            reason="A child supplied personal context and asked to conceal it from the guardian.",
        )

    commercial_context = "commercial_targeting" in request.purpose or _contains_any(request.text, VULNERABILITY_TERMS)
    if commercial_context:
        classifications.extend(["commercial_targeting", "inferred_child_vulnerability"])
        controls.extend(["purpose_limitation", "best_interests_of_child", "human_escalation"])
        return GuardrailResult(
            sanitized_text=sanitized,
            classifications=sorted(set(classifications)),
            controls=sorted(set(controls)),
            blocked=True,
            reason="Commercial targeting based on inferred child vulnerability is prohibited by the demo policy.",
        )

    controls.extend(["data_minimization", "guardian_review_before_child_delivery"])
    return GuardrailResult(
        sanitized_text=sanitized,
        classifications=sorted(set(classifications)) or ["ordinary_family_guidance"],
        controls=sorted(set(controls)),
        blocked=False,
    )


def with_sanitized_text(request: AgentRequest, result: GuardrailResult) -> AgentRequest:
    return replace(request, text=result.sanitized_text)


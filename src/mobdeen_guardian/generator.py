from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class TextGenerator(Protocol):
    def generate(self, system: str, user: str) -> str: ...


@dataclass
class OfflineGenerator:
    """Stable wording for the judged offline demonstration."""

    def generate(self, system: str, user: str) -> str:
        return (
            "خطة أسبوعية مقترحة للمشرف: نشاط قراءة قصير، مهمة مساعدة منزلية بسيطة، "
            "وحوار عائلي عن قيمة التعاون. راجع الخطة ووافق عليها قبل عرضها للطفل."
        )


@dataclass
class OpenAICompatibleGenerator:
    base_url: str
    model: str
    api_key: str
    timeout_seconds: int = 20

    @classmethod
    def from_environment(cls) -> "OpenAICompatibleGenerator":
        return cls(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            model=os.environ["OPENAI_MODEL"],
            api_key=os.environ["OPENAI_API_KEY"],
        )

    def generate(self, system: str, user: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
                "max_tokens": 220,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        return str(body["choices"][0]["message"]["content"]).strip()


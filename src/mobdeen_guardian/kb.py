from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from .models import SourceRef


TOKEN_RE = re.compile(r"[\w\u0600-\u06ff]+", re.UNICODE)
ARABIC_NORMALIZATION = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه"})
STOPWORDS = {
    "the", "and", "or", "a", "an", "to", "of", "in", "for", "with", "is", "are",
    "على", "في", "من", "الى", "إلى", "عن", "او", "أو", "و", "مع", "هذا", "هذه",
}


def tokenize(text: str) -> list[str]:
    folded = text.casefold().translate(ARABIC_NORMALIZATION)
    return [token for token in TOKEN_RE.findall(folded) if len(token) > 1 and token not in STOPWORDS]


def hashed_vector(text: str, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        bucket = int.from_bytes(token.encode("utf-8"), "little", signed=False) % dimensions
        vector[bucket] += 1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


@dataclass(frozen=True)
class SearchHit:
    source: SourceRef
    text: str


class KnowledgeBase:
    def __init__(self, index_path: Path):
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        self.dimensions = int(payload["dimensions"])
        self.chunks = payload["chunks"]

    def search(self, query: str, top_k: int = 4) -> list[SearchHit]:
        query_vector = hashed_vector(query, self.dimensions)
        query_tokens = set(tokenize(query))
        ranked: list[tuple[float, dict]] = []
        for chunk in self.chunks:
            vector_score = cosine(query_vector, chunk["vector"])
            chunk_tokens = set(chunk.get("tokens", []))
            lexical_coverage = len(query_tokens & chunk_tokens) / max(1, len(query_tokens))
            # Exact term coverage carries more weight than the compact hashed
            # vector so collisions cannot push an unrelated source upward.
            score = (0.35 * vector_score) + (0.65 * lexical_coverage)
            if score > 0:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: (-item[0], item[1]["source_id"], item[1]["chunk_id"]))
        hits: list[SearchHit] = []
        for score, chunk in ranked[:top_k]:
            hits.append(
                SearchHit(
                    source=SourceRef(
                        source_id=chunk["source_id"],
                        title=chunk["title"],
                        authority=chunk["authority"],
                        url=chunk["official_url"],
                        section=chunk["section"],
                        score=round(score, 4),
                    ),
                    text=chunk["text"],
                )
            )
        return hits


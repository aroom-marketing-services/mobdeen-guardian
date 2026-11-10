from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mobdeen_guardian.kb import hashed_vector, tokenize  # noqa: E402


def chunks(markdown: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    heading = "Overview"
    buffer: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            if buffer:
                result.append((heading, " ".join(buffer).strip()))
                buffer = []
            heading = line.lstrip("#").strip() or "Overview"
        elif line:
            buffer.append(line)
    if buffer:
        result.append((heading, " ".join(buffer).strip()))
    return [(section, text) for section, text in result if len(text) >= 30]


def main() -> int:
    manifest_path = ROOT / "kb" / "manifest.jsonl"
    entries = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    dimensions = 256
    output_chunks: list[dict] = []
    for entry in entries:
        document_path = ROOT / entry["local_path"]
        text = document_path.read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {entry['source_id']}: {digest}")
        for index, (section, content) in enumerate(chunks(text), start=1):
            vector_text = f"{entry['title']} {entry['use_case_tags']} {section} {content}"
            output_chunks.append(
                {
                    "chunk_id": f"{entry['source_id']}:{index}",
                    "source_id": entry["source_id"],
                    "title": entry["title"],
                    "authority": entry["authority"],
                    "official_url": entry["official_url"],
                    "section": section,
                    "text": content,
                    "tokens": sorted(set(tokenize(vector_text))),
                    "vector": hashed_vector(vector_text, dimensions),
                }
            )
    output_chunks.sort(key=lambda item: item["chunk_id"])
    destination = ROOT / "data" / "index.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps({"schema_version": 1, "dimensions": dimensions, "chunks": output_chunks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Built {len(output_chunks)} chunks from {len(entries)} sources -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


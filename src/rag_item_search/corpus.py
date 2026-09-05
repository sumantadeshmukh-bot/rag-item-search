from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    updated_at: datetime
    max_age_days: int

    def is_stale(self, now: datetime) -> bool:
        age_seconds = (now - self.updated_at).total_seconds()
        return age_seconds > self.max_age_days * 86_400


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_documents(path: Path) -> list[Document]:
    records = json.loads(path.read_text(encoding="utf-8"))
    return [
        Document(
            id=record["id"],
            title=record["title"],
            text=record["text"],
            updated_at=_parse_timestamp(record["updated_at"]),
            max_age_days=int(record["max_age_days"]),
        )
        for record in records
    ]


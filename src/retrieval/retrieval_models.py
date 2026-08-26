from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RetrievedChunk:
    chunk_id: str
    score: float
    text: str
    context: Dict[str, Any]
    chunk_type: str
    page_start: int | None
    page_end: int | None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "score": self.score,
            "text": self.text,
            "context": self.context,
            "chunk_type": self.chunk_type,
            "page_start": self.page_start,
            "page_end": self.page_end,
        }
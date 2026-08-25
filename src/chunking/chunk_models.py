from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import json


@dataclass
class Chunk:
    """
    Canonical RAG chunk representation.

    Every chunk uses the same top-level schema.
    Chunk-specific information is stored inside `context`.
    """

    chunk_id: str
    chunk_index: int
    document_id: str

    chunk_type: str
    text: str

    context: Dict[str, Any]

    page_start: Optional[int] = None
    page_end: Optional[int] = None

    zone: Optional[str] = None
    block_index: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False
        )
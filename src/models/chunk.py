from dataclasses import dataclass, asdict
from typing import Optional
import json


@dataclass
class Chunk:
    chunk_id: str
    chunk_type: str
    text: str

    document_id: str

    part: Optional[str] = None
    part_title: Optional[str] = None

    paragraph: Optional[str] = None
    paragraph_title: Optional[str] = None

    section: Optional[str] = None

    module_code: Optional[str] = None
    module_name: Optional[str] = None

    field: Optional[str] = None

    page_start: Optional[int] = None
    page_end: Optional[int] = None

    zone: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False
        )
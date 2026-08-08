from dataclasses import dataclass
from src.models.block import Block
from src.models.document_zone import DocumentZone
from src.models.section_type import SectionType
from src.models.content_section import ContentSection

@dataclass
class Segment:

    block: Block
    text: str
    order: int
    start: int
    end: int

    zone: DocumentZone | None = None
    section_type: SectionType | None = None
    content_section: ContentSection | None = None
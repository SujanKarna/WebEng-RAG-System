# give the blocks more semantic meaning

from dataclasses import dataclass
from enum import Enum
from src.models.block import Block


class BlockType(Enum):
    TEXT = "text"
    HEADING = "heading"
    TABLE = "table"
    LIST = "list"
   

@dataclass
class DetectedBlock:
    
    block: Block
    type: BlockType
    confidence: float
    level: int | None = None  # For headings, this indicates the heading level (e.g., 1 for H1, 2 for H2, etc.)
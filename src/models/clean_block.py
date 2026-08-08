from dataclasses import dataclass
from enum import Enum

from src.models.block import Block


class BlockRole(Enum):

    CONTENT = "content"
    HEADER = "header"
    FOOTER = "footer"
    PAGE_NUMBER = "page_number"

@dataclass
class CleanBlock:

    block: Block
    role: BlockRole = BlockRole.CONTENT
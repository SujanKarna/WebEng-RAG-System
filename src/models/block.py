# Defining how each block of text is represented
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Block:

    pdf_page: int
    printed_page: int | None = None

    text: str = ""

    x0: float = 0
    y0: float = 0
    x1: float = 0
    y1: float = 0

    font_size: float = 0
    font_name: str = ""

    is_bold: bool = False

    spans: list[dict[str, Any]] = field(default_factory=list)
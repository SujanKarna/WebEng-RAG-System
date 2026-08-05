# Defining how each block of text is represented
from dataclasses import dataclass
from typing import Any

@dataclass
class Block:

    page: int
    text: str

    x0: float
    y0: float
    x1: float
    y1: float

    font_size: float
    font_name: str

    is_bold: bool

    spans: list[dict[str, Any]]
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SourceRange:

    start_page: Optional[int] = None
    end_page: Optional[int] = None

    zone: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def create_source_range(
    start_block: dict,
    end_block: dict | None = None,
) -> SourceRange:

    if end_block is None:
        end_block = start_block

    return SourceRange(
        start_page=start_block.get(
            "page_number"
        ),

        end_page=end_block.get(
            "page_number"
        ),

        zone=start_block.get(
            "zone"
        ),
    )
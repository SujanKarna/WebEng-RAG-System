import json
from pathlib import Path
from typing import List

from src.models.chunk import Chunk


def save_chunks(
    chunks: List[Chunk],
    output_path: Path,
) -> None:
    """
    Persist RAG chunks as JSONL.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for chunk in chunks:

            file.write(
                chunk.to_json()
                + "\n"
            )

    print(
        f"Saved {len(chunks)} chunks to "
        f"{output_path}"
    )
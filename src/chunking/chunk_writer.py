import json
from pathlib import Path
from typing import List

from src.chunking.chunk_models import Chunk


class ChunkWriter:
    """
    Persist canonical RAG chunks as JSONL.

    One chunk is written per line.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    def write(
        self,
        chunks: List[Chunk],
    ) -> None:

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for chunk in chunks:

                file.write(
                    json.dumps(
                        chunk.to_dict(),
                        ensure_ascii=False,
                    )
                    + "\n"
                )
import json
from pathlib import Path
from typing import Any, Dict, List


class EmbeddingWriter:
    """
    Persist chunk embeddings together with
    their original chunk metadata.
    """

    def __init__(
        self,
        path: str,
    ):
        self.path = Path(path)

    def write(
        self,
        records: List[Dict[str, Any]],
    ) -> None:

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                records,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(
            "Embeddings persisted."
        )

        print(
            f"  {self.path}"
        )
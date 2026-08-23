import json
from pathlib import Path
from typing import Dict, List


def save_chunks(
    chunks: List[Dict],
    output_path: Path,
) -> None:
    """
    Persist RAG chunks as JSONL.

    One JSON object is stored per line.

    JSONL is preferable to one huge JSON array because
    vector databases and embedding pipelines can process
    chunks incrementally.
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
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(
        f"Saved {len(chunks)} chunks to "
        f"{output_path}"
    )
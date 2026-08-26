import json
from pathlib import Path

import numpy as np

from src.retrieval.faiss_index import FAISSIndex


def build_faiss_index(
    embeddings_path: str,
    index_directory: str,
) -> None:

    embeddings_path = Path(
        embeddings_path
    )

    # --------------------------------------------------
    # Load persisted embeddings
    # --------------------------------------------------

    with embeddings_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        records = json.load(file)

    if not records:
        raise RuntimeError(
            "No embedding records found."
        )

    print(
        f"Loaded embedding records: "
        f"{len(records)}"
    )

    # --------------------------------------------------
    # Extract vectors
    # --------------------------------------------------

    embeddings = np.asarray(
        [
            record["embedding"]
            for record in records
        ],
        dtype=np.float32,
    )

    # --------------------------------------------------
    # Validate
    # --------------------------------------------------

    if embeddings.ndim != 2:
        raise RuntimeError(
            "Embeddings must form a 2D matrix."
        )

    dimension = embeddings.shape[1]

    print(
        f"Embedding dimension: "
        f"{dimension}"
    )

    # --------------------------------------------------
    # Validate metadata
    # --------------------------------------------------

    metadata = []

    for record in records:

        metadata.append(
            {
                "chunk_id": record[
                    "chunk_id"
                ],

                "chunk_index": record[
                    "chunk_index"
                ],

                "document_id": record[
                    "document_id"
                ],

                "chunk_type": record[
                    "chunk_type"
                ],

                "text": record[
                    "text"
                ],

                "embedding_text": record.get(
                    "embedding_text",
                    "",
                ),

                "context": record.get(
                    "context",
                    {},
                ),

                "page_start": record.get(
                    "page_start"
                ),

                "page_end": record.get(
                    "page_end"
                ),

                "zone": record.get(
                    "zone"
                ),
            }
        )

    # --------------------------------------------------
    # Build index
    # --------------------------------------------------

    index = FAISSIndex(
        dimension=dimension
    )

    index.add(
        embeddings=embeddings,
        metadata=metadata,
    )

    # --------------------------------------------------
    # Validate index size
    # --------------------------------------------------

    if index.index.ntotal != len(
        records
    ):
        raise RuntimeError(
            "FAISS index size does not "
            "match embedding records."
        )

    print(
        f"FAISS vectors indexed: "
        f"{index.index.ntotal}"
    )

    # --------------------------------------------------
    # Persist
    # --------------------------------------------------

    index.save(
        index_directory
    )

    print(
        "FAISS index build completed."
    )



if __name__ == "__main__":

    from pathlib import Path

    PROJECT_ROOT = Path(
        __file__
    ).resolve().parents[2]

    embeddings_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "embeddings.json"
    )

    index_directory = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "vector_index"
    )

    build_faiss_index(
        embeddings_path=str(
            embeddings_path
        ),
        index_directory=str(
            index_directory
        ),
    )
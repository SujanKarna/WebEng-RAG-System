import json
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np


class FAISSIndex:
    """
    FAISS vector index for canonical RAG chunks.

    Uses cosine similarity through normalized
    inner-product search.
    """

    def __init__(
        self,
        dimension: int,
    ):
        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.metadata: List[
            Dict[str, Any]
        ] = []

    # --------------------------------------------------
    # Add vectors
    # --------------------------------------------------

    def add(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
    ) -> None:

        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                "Embedding dimension does not "
                "match index dimension."
            )

        if len(embeddings) != len(metadata):
            raise ValueError(
                "Number of embeddings does not "
                "match metadata entries."
            )

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        # BGE-M3 embeddings were already
        # normalized during embedding.
        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.metadata.extend(
            metadata
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ):

        if self.index.ntotal == 0:
            raise RuntimeError(
                "FAISS index is empty."
            )

        query = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape[1] != self.dimension:
            raise ValueError(
                "Query embedding dimension "
                "does not match index dimension."
            )

        faiss.normalize_L2(query)

        scores, indices = self.index.search(
            query,
            min(
                top_k,
                self.index.ntotal,
            ),
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            results.append(
                {
                    "score": float(score),
                    "metadata": self.metadata[
                        int(index)
                    ],
                }
            )

        return results

    # --------------------------------------------------
    # Persist
    # --------------------------------------------------

    def save(
        self,
        directory: str,
    ) -> None:

        directory = Path(directory)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = (
            directory / "index.faiss"
        )

        metadata_path = (
            directory / "metadata.json"
        )

        faiss.write_index(
            self.index,
            str(index_path),
        )

        with metadata_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.metadata,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(
            "FAISS index persisted."
        )

        print(
            f"  {index_path}"
        )

        print(
            f"  {metadata_path}"
        )

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    @classmethod
    def load(
        cls,
        directory: str,
    ):

        directory = Path(directory)

        index_path = (
            directory / "index.faiss"
        )

        metadata_path = (
            directory / "metadata.json"
        )

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: "
                f"{index_path}"
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata not found: "
                f"{metadata_path}"
            )

        index = faiss.read_index(
            str(index_path)
        )

        with metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            metadata = json.load(file)

        instance = cls(
            dimension=index.d
        )

        instance.index = index
        instance.metadata = metadata

        return instance
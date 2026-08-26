from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class BGEEmbedder:
    """
    Generate normalized embeddings using BAAI/bge-m3.
    """

    MODEL_NAME = "BAAI/bge-m3"

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model_name = model_name

        print(
            f"Loading embedding model: "
            f"{self.model_name}"
        )

        self.model = SentenceTransformer(
            self.model_name
        )

        print(
            "Embedding model loaded."
        )

    def embed(
        self,
        texts: List[str],
    ) -> np.ndarray:

        if not texts:
            return np.empty(
                (0, 0),
                dtype=np.float32,
            )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return embeddings.astype(
            np.float32
        )

    def dimension(self) -> int:
        return self.model.get_embedding_dimension()
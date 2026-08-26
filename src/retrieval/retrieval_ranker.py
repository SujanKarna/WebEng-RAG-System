from typing import List

from src.retrieval.retrieval_models import RetrievedChunk
from src.retrieval.query_analyzer import QueryIntent


class RetrievalRanker:
    """
    Lightweight metadata-aware reranker.

    FAISS provides the semantic similarity score.
    This class adds a small structural preference based
    on the detected query intent.
    """

    INTENT_PREFERENCES = {

        QueryIntent.DURATION: {
            "regulation_paragraph": 1.0,
            "regulation_section": 0.8,
            "module_description": 0.0,
        },

        QueryIntent.ADMISSION: {
            "regulation_paragraph": 1.0,
            "regulation_section": 0.8,
            "module_description": 0.0,
        },

        QueryIntent.PART_TIME: {
            "regulation_paragraph": 1.0,
            "regulation_section": 0.8,
            "module_description": 0.0,
        },

        QueryIntent.EXAMINATION: {
            "module_description": 1.0,
            "regulation_paragraph": 0.8,
            "regulation_section": 0.6,
        },

        QueryIntent.MODULE_CONTENT: {
            "module_description": 1.0,
            "regulation_section": 0.6,
            "regulation_paragraph": 0.4,
        },

        QueryIntent.MODULE_SELECTION: {
            "regulation_section": 1.0,
            "regulation_paragraph": 0.8,
            "module_description": 0.4,
        },

        QueryIntent.GENERAL: {},
    }

    def rank(
        self,
        chunks: List[RetrievedChunk],
        intent: QueryIntent,
    ) -> List[RetrievedChunk]:

        preferences = self.INTENT_PREFERENCES.get(
            intent,
            {},
        )

        if not preferences:
            return chunks

        ranked = []

        for chunk in chunks:

            structural_score = preferences.get(
                chunk.chunk_type,
                0.0,
            )

            # Keep semantic similarity dominant.
            #
            # FAISS score:
            #     ~0.5 - 1.0
            #
            # Structural bonus:
            #     0.0 - 1.0
            #
            # Final score:
            #     85% semantic
            #     15% structural
            #
            final_score = (
                0.85 * chunk.score
                + 0.15 * structural_score
            )

            ranked.append(
                (
                    final_score,
                    chunk,
                )
            )

        ranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            chunk
            for _, chunk in ranked
        ]
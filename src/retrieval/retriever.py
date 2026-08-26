import re
from typing import List

from src.config.settings import (
    RETRIEVAL_CANDIDATE_K,
    RETRIEVAL_KEYWORD_BOOST,
    RETRIEVAL_MIN_SCORE,
    RETRIEVAL_MODULE_BOOST,
    RETRIEVAL_REGULATION_BOOST,
)

from src.retrieval.query_analyzer import QueryAnalyzer
from src.retrieval.retrieval_ranker import RetrievalRanker
from src.embedding.embedder import BGEEmbedder
from src.retrieval.faiss_index import FAISSIndex
from src.retrieval.retrieval_models import RetrievedChunk


class Retriever:
    """
    Semantic retriever using BGE-M3 + FAISS.

    Retrieval pipeline:

        Query
          ↓
        BGE-M3 embedding
          ↓
        FAISS candidate retrieval
          ↓
        Metadata boost
          ↓
        Keyword / topic boost
          ↓
        RetrievalRanker
          ↓
        RetrievedChunk objects
    """

    def __init__(
        self,
        index_directory: str,
        embedder: BGEEmbedder | None = None,
    ):

        self.index = FAISSIndex.load(
            index_directory
        )

        self.embedder = (
            embedder
            if embedder is not None
            else BGEEmbedder()
        )

        self.query_analyzer = QueryAnalyzer()
        self.ranker = RetrievalRanker()

    # ==========================================================
    # PUBLIC RETRIEVAL
    # ==========================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[RetrievedChunk]:

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        # ------------------------------------------------------
        # 1. Embed query
        # ------------------------------------------------------

        query_embedding = self.embedder.embed(
            [query]
        )

        # ------------------------------------------------------
        # 2. Retrieve larger candidate pool
        # ------------------------------------------------------

        candidate_k = max(
            top_k * 2,
            RETRIEVAL_CANDIDATE_K,
        )

        results = self.index.search(
            query_embedding,
            top_k=candidate_k,
        )

        # ------------------------------------------------------
        # 3. Calculate retrieval score
        # ------------------------------------------------------

        reranked = []

        for result in results:

            metadata = result["metadata"]

            semantic_score = result["score"]

            metadata_boost = self._metadata_boost(
                metadata
            )

            keyword_boost = self._keyword_boost(
                query,
                metadata,
            )

            retrieval_score = (
                semantic_score
                + metadata_boost
                + keyword_boost
            )

            reranked.append(
                (
                    retrieval_score,
                    result,
                )
            )

        # ------------------------------------------------------
        # 4. Sort
        # ------------------------------------------------------

        reranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # ------------------------------------------------------
        # 5. Build RetrievedChunk objects
        # ------------------------------------------------------

        retrieved = []

        for retrieval_score, result in reranked:

            metadata = result["metadata"]

            retrieved.append(
                RetrievedChunk(
                    chunk_id=metadata["chunk_id"],

                    score=float(
                        retrieval_score
                    ),

                    text=metadata["text"],

                    context=metadata.get(
                        "context",
                        {},
                    ),

                    chunk_type=metadata[
                        "chunk_type"
                    ],

                    page_start=metadata.get(
                        "page_start"
                    ),

                    page_end=metadata.get(
                        "page_end"
                    ),
                )
            )

        # ------------------------------------------------------
        # 6. Existing intent-based ranking
        # ------------------------------------------------------

        intent = self.query_analyzer.analyze(
            query
        )

        ranked = self.ranker.rank(
            chunks=retrieved,
            intent=intent,
        )

        return ranked[:top_k]

    # ==========================================================
    # METADATA BOOST
    # ==========================================================

    def _metadata_boost(
        self,
        metadata: dict,
    ) -> float:

        chunk_type = (
            metadata.get(
                "chunk_type",
                "",
            )
            .lower()
        )

        boost = 0.0

        if "regulation" in chunk_type:

            boost += (
                RETRIEVAL_REGULATION_BOOST
            )

        elif "module" in chunk_type:

            boost += (
                RETRIEVAL_MODULE_BOOST
            )

        return boost

    # ==========================================================
    # KEYWORD / TOPIC BOOST
    # ==========================================================

    def _keyword_boost(
        self,
        query: str,
        metadata: dict,
    ) -> float:

        text = metadata.get(
            "text",
            "",
        )

        if not text:
            return 0.0

        # ------------------------------------------------------
        # Extract normal query terms
        # ------------------------------------------------------

        query_terms = self._extract_terms(
            query
        )

        # ------------------------------------------------------
        # Add related terms for common question types
        # ------------------------------------------------------

        query_terms.extend(
            self._expand_query_terms(query)
        )

        # Remove duplicates
        query_terms = list(
            dict.fromkeys(query_terms)
        )

        if not query_terms:
            return 0.0

        text_lower = text.lower()

        # ------------------------------------------------------
        # Count matching terms
        # ------------------------------------------------------

        matches = sum(
            1
            for term in query_terms
            if term in text_lower
        )

        if matches == 0:
            return 0.0

        match_ratio = (
            matches
            / len(query_terms)
        )

        return (
            RETRIEVAL_KEYWORD_BOOST
            * match_ratio
        )

    # ==========================================================
    # QUERY EXPANSION
    # ==========================================================

    @staticmethod
    def _expand_query_terms(
        query: str,
    ) -> List[str]:

        """
        Adds a small number of domain-independent
        German synonyms / related terms.

        This is intentionally simple.

        Example:

            "Wie lange dauert das Studium?"

        becomes additionally associated with:

            regelstudienzeit
            semester
            jahre
            dauer
        """

        query_lower = query.lower()

        expanded_terms = []

        # ------------------------------------------------------
        # Study duration
        # ------------------------------------------------------

        duration_patterns = [
            "wie lange",
            "dauer",
            "dauert",
            "studienzeit",
            "regelstudienzeit",
        ]

        if any(
            pattern in query_lower
            for pattern in duration_patterns
        ):

            expanded_terms.extend(
                [
                    "regelstudienzeit",
                    "studienzeit",
                    "semester",
                    "jahre",
                    "dauer",
                ]
            )

        # ------------------------------------------------------
        # Admission requirements
        # ------------------------------------------------------

        admission_patterns = [
            "voraussetzung",
            "voraussetzungen",
            "zulassung",
            "zugang",
            "zugelassen",
        ]

        if any(
            pattern in query_lower
            for pattern in admission_patterns
        ):

            expanded_terms.extend(
                [
                    "zugangsvoraussetzungen",
                    "voraussetzungen",
                    "zulassung",
                    "abschluss",
                    "bachelor",
                    "b2",
                ]
            )

        # ------------------------------------------------------
        # Part-time study
        # ------------------------------------------------------

        part_time_patterns = [
            "teilzeit",
            "teilzeitstudium",
            "teilzeitstudium",
        ]

        if any(
            pattern in query_lower
            for pattern in part_time_patterns
        ):

            expanded_terms.extend(
                [
                    "teilzeit",
                    "teilzeitstudium",
                    "arbeitsaufwand",
                    "semester",
                ]
            )

        # ------------------------------------------------------
        # Modules
        # ------------------------------------------------------

        module_patterns = [
            "modul",
            "module",
            "grundlagenmodul",
            "grundlagenmodule",
        ]

        if any(
            pattern in query_lower
            for pattern in module_patterns
        ):

            expanded_terms.extend(
                [
                    "modul",
                    "module",
                ]
            )

        # ------------------------------------------------------
        # Examination
        # ------------------------------------------------------

        exam_patterns = [
            "prüfung",
            "prüfungsleistung",
            "prüfungsleistungen",
            "prüfungleistung",
            "klausur",
            "examen",
        ]

        if any(
            pattern in query_lower
            for pattern in exam_patterns
        ):

            expanded_terms.extend(
                [
                    "prüfung",
                    "prüfungsleistung",
                    "klausur",
                    "prüfung",
                ]
            )

        return expanded_terms

    # ==========================================================
    # TERM EXTRACTION
    # ==========================================================

    @staticmethod
    def _extract_terms(
        text: str,
    ) -> List[str]:

        words = re.findall(
            r"[a-zA-ZäöüÄÖÜß0-9]+",
            text.lower(),
        )

        stopwords = {
            "der",
            "die",
            "das",
            "den",
            "dem",
            "des",
            "ein",
            "eine",
            "einer",
            "einem",
            "einen",
            "und",
            "oder",
            "für",
            "von",
            "zu",
            "zum",
            "zur",
            "im",
            "in",
            "ist",
            "sind",
            "wie",
            "was",
            "gilt",
            "gelten",
            "man",
            "es",
            "sich",
            "wer",
            "welche",
            "welcher",
            "welches",
            "wird",
            "werden",
            "denn",
            "über",
            "auf",
            "an",
            "mit",
        }

        return [
            word
            for word in words
            if len(word) >= 3
            and word not in stopwords
        ]
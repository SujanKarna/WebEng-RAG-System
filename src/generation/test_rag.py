from src.config.settings import (
    FAISS_INDEX_DIR,
)

from src.generation.rag_pipeline import (
    RAGPipeline,
)


def main():

    print("=" * 80)
    print("RAG PIPELINE TEST")
    print("=" * 80)

    print("\nInitializing RAG pipeline...")

    rag = RAGPipeline(
        index_directory=str(
            FAISS_INDEX_DIR
        )
    )

    print("RAG pipeline initialized.")

    queries = [
        "Welche Voraussetzungen gelten für die Zulassung zum Masterstudiengang Web Engineering?",
        "Wie lange dauert das Studium Web Engineering?",
        "Welche Module gehören zu den Grundlagenmodulen?",
        "Was lernt man im Modul Advanced Management of Data?",
        "Was gilt für ein Teilzeitstudium?",
    ]

    for query in queries:

        print("\n")
        print("=" * 80)
        print(f"QUESTION: {query}")
        print("=" * 80)

        answer, sources = rag.answer_with_sources(
            query
        )

        print("\nANSWER")
        print("-" * 80)
        print(answer)

        print("\nSOURCES")
        print("-" * 80)

        for index, source in enumerate(
            sources,
            start=1,
        ):

            print(
                f"[{index}] "
                f"{source.chunk_id} "
                f"(score={source.score:.4f})"
            )


if __name__ == "__main__":
    main()
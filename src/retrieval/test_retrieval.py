from pathlib import Path

from src.retrieval.retriever import Retriever


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

INDEX_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "vector_index"
)


def print_results(
    query: str,
    results,
) -> None:

    print()
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print()
        print(
            f"[{rank}] "
            f"{result.chunk_id}"
        )

        print(
            f"Score: "
            f"{result.score:.4f}"
        )

        print(
            f"Type: "
            f"{result.chunk_type}"
        )

        context = result.context

        if context.get("paragraph"):
            print(
                f"Paragraph: "
                f"{context['paragraph']}"
            )

        if context.get("paragraph_title"):
            print(
                f"Title: "
                f"{context['paragraph_title']}"
            )

        if context.get("module_code"):
            print(
                f"Module: "
                f"{context['module_code']} "
                f"— "
                f"{context.get('module_name', '')}"
            )

        print(
            f"Text: "
            f"{result.text[:500]}"
        )


def main():

    print("=" * 80)
    print("RETRIEVAL TEST")
    print("=" * 80)

    retriever = Retriever(
        index_directory=str(
            INDEX_DIRECTORY
        )
    )

    test_queries = [
        (
            "Welche Voraussetzungen "
            "gelten für die Zulassung zum "
            "Masterstudiengang Web Engineering?"
        ),

        (
            "Wie lange dauert das Studium "
            "Web Engineering?"
        ),

        (
            "Welche Module gehören zu "
            "den Grundlagenmodulen?"
        ),

        (
            "Was lernt man im Modul "
            "Advanced Management of Data?"
        ),

        (
            "Welche Prüfungsleistung gibt es "
            "im Modul Software Service Engineering?"
        ),

        (
            "Was gilt für ein Teilzeitstudium?"
        ),
    ]

    for query in test_queries:

        results = retriever.retrieve(
            query=query,
            top_k=5,
        )

        print_results(
            query,
            results,
        )


if __name__ == "__main__":
    main()
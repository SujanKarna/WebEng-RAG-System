import json
from pathlib import Path
from typing import Any


def save_regulation_structure(
    regulation: dict[str, Any],
    output_path: str | Path,
) -> None:
    """
    Persist the complete structured regulation as JSON.

    The regulation structure is assumed to contain only
    JSON-serializable values.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            regulation,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Regulation structure saved: "
        f"{output_path}"
    )
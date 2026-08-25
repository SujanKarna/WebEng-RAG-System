import json
from pathlib import Path
from typing import Any


class NormalizedMainRegulationWriter:
    """
    Persists the normalized main regulation.

    The normalized main regulation is produced by
    MainRegulationNormalizer and contains the cleaned,
    structured representation of the main regulation.

    This writer performs no transformation.
    """

    def __init__(
        self,
        output_path: Path,
    ):
        self.output_path = output_path

    def write(
        self,
        regulation: list[dict[str, Any]],
    ) -> None:

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                regulation,
                file,
                ensure_ascii=False,
                indent=2,
            )
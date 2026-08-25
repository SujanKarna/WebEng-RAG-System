import json
from pathlib import Path
from typing import Any


class CombinedRegulationWriter:
    """
    Persists the combined regulation structure.

    The combined structure contains the parsed regulation
    together with normalized module descriptions attached
    to §6 module references.
    """

    def __init__(
        self,
        output_path: Path,
    ):
        self.output_path = output_path

    def write(
        self,
        regulation: dict[str, Any],
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

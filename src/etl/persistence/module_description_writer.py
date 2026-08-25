import json
from dataclasses import asdict
from pathlib import Path
from typing import Any


class ModuleDescriptionWriter:

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def write(
        self,
        modules: list[Any],
    ) -> None:

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = [
            asdict(module)
            for module in modules
        ]

        with self.output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
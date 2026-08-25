import copy
from typing import Any


class CombinedRegulationBuilder:
    """
    Pure composition step.

    Combines:
      1. normalized main regulation
      2. normalized module descriptions

    No PDF parsing, cleaning, normalization, classification,
    or interpretation is performed here.
    """

    def build(
        self,
        main_regulation: list[dict[str, Any]],
        module_descriptions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        module_index = self._index_modules(module_descriptions)

        regulation = copy.deepcopy(main_regulation)

        for paragraph in regulation:

            if paragraph.get("paragraph") != "§ 6":
                continue

            self._attach_module_descriptions(
                paragraph=paragraph,
                module_index=module_index,
            )

        return regulation

    @staticmethod
    def _index_modules(
        module_descriptions: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:

        return {
            module["module_code"]: module
            for module in module_descriptions
            if module.get("module_code")
        }

    def _attach_module_descriptions(
        self,
        paragraph: dict[str, Any],
        module_index: dict[str, dict[str, Any]],
    ) -> None:

        for group in paragraph.get("module_groups", []):

            for module_ref in group.get("modules", []):

                module_code = module_ref.get("module_code")

                if not module_code:
                    continue

                module_description = module_index.get(module_code)

                if module_description is None:
                    continue

                module_ref["description"] = copy.deepcopy(
                    module_description
                )
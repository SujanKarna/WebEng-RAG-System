from src.etl.models.normalized_module_description import (
    NormalizedModuleDescription,
)


def build_module_description_index(
    descriptions: list[NormalizedModuleDescription],
) -> dict[str, NormalizedModuleDescription]:
    """
    Build a lookup index for normalized module descriptions.

    The module code is the canonical relationship key between
    §6 module entries and their detailed module descriptions.
    """

    index: dict[str, NormalizedModuleDescription] = {}

    for description in descriptions:

        if not description.module_code:
            continue

        index[description.module_code] = description

    return index
from typing import Any, Dict, List


DOCUMENT_ID = "tu_chemnitz_web_engineering_2025"


# ============================================================
# MAIN REGULATION CONTEXT
# ============================================================

def build_regulation_context(
    paragraph: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build retrieval context for a main-regulation paragraph.

    The normalized main regulation is the authoritative source
    for curriculum structure and regulatory information.
    """

    context: Dict[str, Any] = {}

    if paragraph.get("part"):
        context["part"] = paragraph["part"]

    if paragraph.get("part_title"):
        context["part_title"] = paragraph["part_title"]

    if paragraph.get("paragraph"):
        context["paragraph"] = paragraph["paragraph"]

    if paragraph.get("paragraph_title"):
        context["paragraph_title"] = paragraph[
            "paragraph_title"
        ]

    return context


# ============================================================
# SECTION CONTEXT
# ============================================================

def build_section_context(
    paragraph: Dict[str, Any],
    section: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build hierarchical context for a regulation section.
    """

    context = build_regulation_context(
        paragraph
    )

    if section.get("number") is not None:
        context["section"] = section["number"]

    if section.get("title"):
        context["section_title"] = section[
            "title"
        ]

    return context


# ============================================================
# MODULE CONTEXT
# ============================================================

def build_module_context(
    paragraph: Dict[str, Any],
    section: Dict[str, Any],
    module: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build complete curriculum context for a module.

    This context connects a module description to its
    position and role in the main study regulation.
    """

    context = build_section_context(
        paragraph,
        section,
    )

    if module.get("module_code"):
        context["module_code"] = module[
            "module_code"
        ]

    if module.get("module_name"):
        context["module_name"] = module[
            "module_name"
        ]

    if module.get("credits") is not None:
        context["credits"] = module[
            "credits"
        ]

    if module.get("requirement"):
        context["requirement"] = module[
            "requirement"
        ]

    return context


# ============================================================
# MODULE CURRICULUM INDEX
# ============================================================

def build_module_curriculum_index(
    regulation: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Build a lookup index from module code to curriculum context.

    Example:

        {
            "257070-003": {
                "part": "...",
                "paragraph": "§ 6",
                "section": "2",
                "section_title": "Vertiefungsmodule",
                "module_code": "257070-003",
                "module_name": "Empirical Software Engineering",
                "credits": 5,
                "requirement": "Wahlpflichtmodul"
            }
        }

    The normalized main regulation is treated as the
    authoritative curriculum source.
    """

    index: Dict[str, Dict[str, Any]] = {}

    if not isinstance(regulation, list):
        return index

    for paragraph in regulation:

        if not isinstance(paragraph, dict):
            continue

        sections = paragraph.get(
            "sections",
            []
        )

        if not isinstance(sections, list):
            continue

        for section in sections:

            if not isinstance(section, dict):
                continue

            # ------------------------------------------------
            # Regular modules
            # ------------------------------------------------

            modules = section.get(
                "modules",
                []
            )

            if isinstance(modules, list):

                for module in modules:

                    if not isinstance(
                        module,
                        dict,
                    ):
                        continue

                    module_code = module.get(
                        "module_code"
                    )

                    if not module_code:
                        continue

                    index[module_code] = (
                        build_module_context(
                            paragraph,
                            section,
                            module,
                        )
                    )

            # ------------------------------------------------
            # Selection groups
            # ------------------------------------------------

            selection_groups = section.get(
                "selection_groups",
                []
            )

            if isinstance(
                selection_groups,
                list,
            ):

                for group in selection_groups:

                    if not isinstance(
                        group,
                        dict,
                    ):
                        continue

                    group_modules = group.get(
                        "modules",
                        []
                    )

                    if not isinstance(
                        group_modules,
                        list,
                    ):
                        continue

                    for module in group_modules:

                        if not isinstance(
                            module,
                            dict,
                        ):
                            continue

                        module_code = module.get(
                            "module_code"
                        )

                        if not module_code:
                            continue

                        context = (
                            build_module_context(
                                paragraph,
                                section,
                                module,
                            )
                        )

                        context[
                            "selection_group"
                        ] = True

                        context[
                            "selection_type"
                        ] = group.get(
                            "selection_type"
                        )

                        index[module_code] = (
                            context
                        )

            # ------------------------------------------------
            # Conditional modules
            # ------------------------------------------------

            conditional_modules = (
                section.get(
                    "conditional_modules",
                    []
                )
            )

            if isinstance(
                conditional_modules,
                list,
            ):

                for conditional in (
                    conditional_modules
                ):

                    if not isinstance(
                        conditional,
                        dict,
                    ):
                        continue

                    module = conditional.get(
                        "module"
                    )

                    if not isinstance(
                        module,
                        dict,
                    ):
                        continue

                    module_code = module.get(
                        "module_code"
                    )

                    if not module_code:
                        continue

                    context = (
                        build_module_context(
                            paragraph,
                            section,
                            module,
                        )
                    )

                    context[
                        "conditional"
                    ] = True

                    if conditional.get(
                        "condition"
                    ):
                        context[
                            "condition"
                        ] = conditional[
                            "condition"
                        ]

                    index[module_code] = (
                        context
                    )

    return index
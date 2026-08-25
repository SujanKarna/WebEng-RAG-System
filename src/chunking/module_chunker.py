from typing import Any, Dict, List

from src.chunking.chunk_models import Chunk

from src.chunking.context_builder import (
    DOCUMENT_ID,
    build_module_curriculum_index,
)


# ============================================================
# MODULE TEXT
# ============================================================

def _build_module_text(
    module: Dict[str, Any],
) -> str:
    """
    Build a context-rich textual representation of one
    normalized module description.

    The persisted normalized module is the source of truth.
    """

    parts = []

    # --------------------------------------------------------
    # Module identity
    # --------------------------------------------------------

    module_code = module.get(
        "module_code"
    )

    module_name = module.get(
        "module_name"
    )

    if module_code or module_name:

        header = "Module"

        if module_code:
            header += f": {module_code}"

        if module_name:
            header += f" — {module_name}"

        parts.append(
            header
        )

    # --------------------------------------------------------
    # Module metadata
    # --------------------------------------------------------

    category = module.get(
        "category"
    )

    if category:
        parts.append(
            f"Category:\n{category}"
        )

    version = module.get(
        "version"
    )

    if version:
        parts.append(
            f"Version:\n{version}"
        )

    responsible = module.get(
        "responsible"
    )

    if responsible:
        parts.append(
            f"Responsible:\n{responsible}"
        )

    # --------------------------------------------------------
    # Academic content
    # --------------------------------------------------------

    fields = [
        (
            "content",
            "Content",
        ),
        (
            "qualification_goals",
            "Qualification Goals",
        ),
        (
            "teaching_forms",
            "Teaching Forms",
        ),
        (
            "prerequisites",
            "Prerequisites",
        ),
        (
            "applicability",
            "Applicability",
        ),
        (
            "credit_requirements",
            "Credit Requirements",
        ),
        (
            "examination",
            "Examination",
        ),
        (
            "credits_and_grades",
            "Credits and Grades",
        ),
        (
            "frequency",
            "Frequency",
        ),
        (
            "workload",
            "Workload",
        ),
        (
            "duration",
            "Duration",
        ),
    ]

    for key, label in fields:

        value = module.get(
            key
        )

        if value is None:
            continue

        if isinstance(value, str):

            value = value.strip()

            if not value:
                continue

            parts.append(
                f"{label}:\n{value}"
            )

        else:

            parts.append(
                f"{label}:\n{value}"
            )

    return "\n\n".join(
        parts
    ).strip()


# ============================================================
# MODULE CHUNKING
# ============================================================

def chunk_module_descriptions(
    modules: List[Dict[str, Any]],
    regulation: List[Dict[str, Any]],
) -> List[Chunk]:
    """
    Convert normalized module descriptions into canonical
    RAG chunks.

    Each complete module description remains one semantic
    chunk.

    Curriculum context is resolved from the persisted
    normalized main regulation.
    """

    chunks: List[Chunk] = []

    # --------------------------------------------------------
    # Build curriculum lookup
    # --------------------------------------------------------

    curriculum_index = (
        build_module_curriculum_index(
            regulation
        )
    )

    print(
        f"Curriculum module index: "
        f"{len(curriculum_index)} modules"
    )

    # --------------------------------------------------------
    # Process modules
    # --------------------------------------------------------

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

        text = _build_module_text(
            module
        )

        if not text:
            continue

        # ----------------------------------------------------
        # Module description context
        # ----------------------------------------------------

        context: Dict[str, Any] = {
            "module_code": module_code,
        }

        if module.get("module_name"):
            context["module_name"] = (
                module["module_name"]
            )

        if module.get("category"):
            context["category"] = (
                module["category"]
            )

        if module.get("version"):
            context["version"] = (
                module["version"]
            )

        if module.get("responsible"):
            context["responsible"] = (
                module["responsible"]
            )

        if module.get("credits") is not None:
            context["credits"] = (
                module["credits"]
            )

        if module.get("workload_as") is not None:
            context["workload_as"] = (
                module["workload_as"]
            )

        if module.get(
            "duration_semesters"
        ) is not None:

            context[
                "duration_semesters"
            ] = module[
                "duration_semesters"
            ]

        # ----------------------------------------------------
        # Curriculum context
        # ----------------------------------------------------

        curriculum_context = (
            curriculum_index.get(
                module_code
            )
        )

        if curriculum_context:

            context[
                "curriculum"
            ] = curriculum_context

        else:

            context[
                "curriculum"
            ] = None

            context[
                "curriculum_reference_missing"
            ] = True

        # ----------------------------------------------------
        # Source information
        # ----------------------------------------------------

        source = module.get(
            "source"
        )

        page_start = None
        page_end = None
        zone = None

        if isinstance(
            source,
            dict,
        ):

            page_start = source.get(
                "start_page"
            )

            page_end = source.get(
                "end_page"
            )

            zone = source.get(
                "zone"
            )

            context[
                "source"
            ] = source

        # ----------------------------------------------------
        # Create canonical chunk
        # ----------------------------------------------------

        chunk = Chunk(

            chunk_id=(
                f"module_{module_code}"
            ),

            chunk_index=len(
                chunks
            ),

            document_id=DOCUMENT_ID,

            chunk_type=(
                "module_description"
            ),

            text=text,

            context=context,

            page_start=page_start,

            page_end=page_end,

            zone=zone,
        )

        chunks.append(
            chunk
        )

    return chunks
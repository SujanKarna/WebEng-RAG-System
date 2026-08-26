from enum import Enum


class QueryIntent(str, Enum):
    GENERAL = "general"
    DURATION = "duration"
    ADMISSION = "admission"
    MODULE_SELECTION = "module_selection"
    MODULE_CONTENT = "module_content"
    EXAMINATION = "examination"
    PART_TIME = "part_time"


class QueryAnalyzer:
    """
    Lightweight rule-based query intent classifier.

    This is intentionally deterministic. We use it to improve
    retrieval without introducing another ML model.
    """

    def analyze(self, query: str) -> QueryIntent:

        q = query.lower().strip()

        # ---------------------------------------------
        # Admission
        # ---------------------------------------------

        admission_keywords = [
            "zulassung",
            "zugangsvoraussetzung",
            "voraussetzungen",
            "bewerbung",
            "bewerber",
            "zugang",
        ]

        if any(
            keyword in q
            for keyword in admission_keywords
        ):
            return QueryIntent.ADMISSION

        # ---------------------------------------------
        # Duration
        # ---------------------------------------------

        duration_keywords = [
            "wie lange",
            "dauer",
            "regelstudienzeit",
            "semester",
            "jahre",
            "studienbeginn",
        ]

        if any(
            keyword in q
            for keyword in duration_keywords
        ):
            return QueryIntent.DURATION

        # ---------------------------------------------
        # Part-time
        # ---------------------------------------------

        part_time_keywords = [
            "teilzeit",
            "teilzeitstudium",
            "teilzeit studium",
            "berufstätigkeit",
        ]

        if any(
            keyword in q
            for keyword in part_time_keywords
        ):
            return QueryIntent.PART_TIME

        # ---------------------------------------------
        # Examination
        # ---------------------------------------------

        examination_keywords = [
            "prüfungsleistung",
            "prüfung",
            "klausur",
            "prüfungsvoraussetzung",
            "prüfungsform",
        ]

        if any(
            keyword in q
            for keyword in examination_keywords
        ):
            return QueryIntent.EXAMINATION

        # ---------------------------------------------
        # Module content
        # ---------------------------------------------

        module_content_keywords = [
            "was lernt man",
            "was lernt",
            "inhalte des moduls",
            "modulinhalt",
            "inhalt des moduls",
            "qualification goals",
            "qualifikationsziele",
        ]

        if any(
            keyword in q
            for keyword in module_content_keywords
        ):
            return QueryIntent.MODULE_CONTENT

        # ---------------------------------------------
        # Module selection
        # ---------------------------------------------

        module_selection_keywords = [
            "welche module",
            "module gehören",
            "module gibt es",
            "grundlagenmodule",
            "vertiefungsmodule",
            "challengemodule",
            "schlüsselkompetenzen",
        ]

        if any(
            keyword in q
            for keyword in module_selection_keywords
        ):
            return QueryIntent.MODULE_SELECTION

        return QueryIntent.GENERAL
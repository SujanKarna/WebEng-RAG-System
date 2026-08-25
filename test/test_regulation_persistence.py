import json

from src.etl.parser.regulation.regulation_parser import RegulationParser
from src.etl.persistence.regulation_writer import RegulationWriter
from src.config.settings import CLEANED_BLOCKS_PATH
from src.config.settings import PARSED_REGULATION_PATH


def main():

    with CLEANED_BLOCKS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        blocks = json.load(file)

    parser = RegulationParser(blocks)

    paragraphs = parser.parse()

    print(
        f"Paragraphs extracted: {len(paragraphs)}"
    )

    writer = RegulationWriter(
        PARSED_REGULATION_PATH
    )

    writer.write(paragraphs)

    print(
        f"Written to: {PARSED_REGULATION_PATH}"
    )


if __name__ == "__main__":
    main()
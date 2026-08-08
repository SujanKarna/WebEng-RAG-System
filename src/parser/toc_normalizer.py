# Paragraph lines were in a single line so this function will seprate them into seprate lines

import re
import copy



def split_toc_sections(segments):

    new_segments = []


    for segment in segments:

        if segment.zone.name != "TOC":

            new_segments.append(segment)
            continue


        text = segment.text.strip()


        # Find all § entries
        matches = list(
            re.finditer(
                r'§\s*\d+[^§]*',
                text
            )
        )


        # No § entries or only one
        if len(matches) <= 1:

            new_segments.append(segment)
            continue


        for match in matches:

            new_segment = copy.copy(segment)

            new_segment.text = match.group().strip()

            new_segments.append(
                new_segment
            )


    return new_segments
from __future__ import annotations
from src.models.segment import Segment
from dataclasses import dataclass, field
from src.models.section_type import SectionType




@dataclass
class DocumentNode:

    segment: object | None = None

    title: str | None = None

    node_type: object | None = None

    text: str | None = None

    parent: "DocumentNode | None" = None

    children: list["DocumentNode"] = field(
        default_factory=list
    )

    def add_child(self, node):

        """
        Attach child node and maintain parent relation.
        """

        node.parent = self

        self.children.append(node)

        

    def __post_init__(self):

        if self.segment:

            self.title = (
                self.segment.text
            )

            self.node_type = (
                self.segment.section_type
            )


            if (
                self.segment.section_type
                == SectionType.TEXT
            ):

                self.text = (
                    self.segment.text
                )
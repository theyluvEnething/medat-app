"""Data models for MedAT KFF questions."""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


class Section(StrEnum):
    FIGUREN = "figuren"
    ZAHLENFOLGEN = "zahlenfolgen"
    WORTFLUESSIGKEIT = "wortfluessigkeit"
    IMPLIKATIONEN = "implikationen"
    AUSWEISE = "ausweise"


SECTION_META: dict[Section, dict[str, int | str]] = {
    Section.FIGUREN: {"time_min": 20, "count": 15, "label": "Figuren zusammensetzen"},
    Section.ZAHLENFOLGEN: {"time_min": 15, "count": 10, "label": "Zahlenfolgen"},
    Section.WORTFLUESSIGKEIT: {"time_min": 20, "count": 15, "label": "Wortflüssigkeit"},
    Section.IMPLIKATIONEN: {"time_min": 10, "count": 10, "label": "Implikationen erkennen"},
    Section.AUSWEISE: {"time_min": 8, "count": 25, "label": "Ausweise Merken"},
}


class Question(BaseModel):
    section: Section
    id: int
    answer: str
    content: str  # text or relative image path


class QuestionSet(BaseModel):
    figuren: list[Question]
    zahlenfolgen: list[Question]
    wortfluessigkeit: list[Question]
    implikationen: list[Question]
    ausweise: list[Question]

    @classmethod
    def from_json(cls, path: Path) -> "QuestionSet":
        import json

        with open(path, encoding="utf-8") as f:
            return cls.model_validate(json.load(f))

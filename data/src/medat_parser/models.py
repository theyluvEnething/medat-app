"""Data models for MedAT KFF questions."""

from __future__ import annotations

from enum import StrEnum


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
    Section.IMPLIKATIONEN: {
        "time_min": 10,
        "count": 10,
        "label": "Implikationen erkennen",
    },
    Section.AUSWEISE: {"time_min": 8, "count": 25, "label": "Ausweise Merken"},
}

# Zero-padding for each section's global ID in filenames
SECTION_ID_PAD: dict[Section, int] = {
    Section.FIGUREN: 3,
    Section.ZAHLENFOLGEN: 2,
    Section.WORTFLUESSIGKEIT: 4,
    Section.IMPLIKATIONEN: 2,
    Section.AUSWEISE: 4,  # recall questions; cards use 3
}

# Questions per set for each section
SECTION_SET_SIZE: dict[Section, int] = {
    Section.FIGUREN: 15,
    Section.ZAHLENFOLGEN: 10,
    Section.WORTFLUESSIGKEIT: 15,
    Section.IMPLIKATIONEN: 10,
    Section.AUSWEISE: 25,  # recall questions; cards use 8
}

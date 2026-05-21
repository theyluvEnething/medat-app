"""Shared utilities for MedAT PDF parsers."""

from __future__ import annotations


def words_to_text(words: list, tolerance: float = 3.0) -> str:
    """Reconstruct text from pdfplumber word objects, preserving line breaks.

    Groups words by rounded y-position so line detection is robust to
    non-sequential word ordering from pdfplumber.
    """
    if not words:
        return ""

    lines: dict[int, list[str]] = {}
    for w in words:
        top = round(w["top"], 0)
        if top not in lines:
            lines[top] = []
        lines[top].append(w["text"])

    return "\n".join(" ".join(lines[top]) for top in sorted(lines))

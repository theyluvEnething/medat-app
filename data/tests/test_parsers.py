"""Verify the regex patterns used to extract answer keys from PDF text."""

from __future__ import annotations

import re


def test_implikationen_answer_regex() -> None:
    text = "1. D 2. E 3. C 10. A 11. B"
    matches = re.findall(r"(\d+)\.\s*([A-E])", text)
    result = {int(m[0]): m[1] for m in matches}
    assert result[1] == "D"
    assert result[2] == "E"
    assert result[10] == "A"
    assert result[11] == "B"
    assert len(result) == 5


def test_wortfluessigkeit_answer_regex() -> None:
    text = "1. C EHEFRAU 2. C TESTUNG 15. A KRANKENHAUS"
    matches = re.finditer(r"(\d+)\.\s+([A-E])\s+(\S+)", text)
    results = {}
    for m in matches:
        results[int(m.group(1))] = {"letter": m.group(2), "word": m.group(3)}
    assert results[1] == {"letter": "C", "word": "EHEFRAU"}
    assert results[2] == {"letter": "C", "word": "TESTUNG"}
    assert results[15] == {"letter": "A", "word": "KRANKENHAUS"}


def test_zahlenfolgen_answer_regex() -> None:
    text = (
        "1. C 71/90 A₄=A₂+A₁,A₅=A₃+A₂,...\n"
        "2. D 15/32 Verdopplung\n"
        "3. B 7/13 Primzahlen"
    )
    matches = re.finditer(r"(\d+)\.\s+([A-E])\s+(\S+)\s+(.*?)(?=\n\d+\.|\Z)", text, re.DOTALL)
    results = {}
    for m in matches:
        results[int(m.group(1))] = {
            "letter": m.group(2),
            "value": m.group(3),
            "explanation": m.group(4).strip(),
        }
    assert results[1]["letter"] == "C"
    assert results[1]["value"] == "71/90"
    assert results[2]["value"] == "15/32"
    assert results[3]["value"] == "7/13"


def test_figuren_answer_regex() -> None:
    text = "1. C 2. D 3. A 105. B"
    matches = re.findall(r"(\d+)\.\s*([A-E])(?=[\s,]|$)", text)
    result = {int(m[0]): m[1] for m in matches}
    assert result[1] == "C"
    assert result[105] == "B"

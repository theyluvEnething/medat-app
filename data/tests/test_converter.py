"""Verify the converter reads flat file output and produces questions.json."""

from __future__ import annotations

import json
from pathlib import Path

from medat_parser.converter import _parse_id, convert


def test_parse_id_figuren() -> None:
    assert _parse_id("001_question.txt", 3) == 1
    assert _parse_id("255_question.txt", 3) == 255
    assert _parse_id("01_question.txt", 3) is None  # wrong padding


def test_parse_id_implikationen() -> None:
    assert _parse_id("01_question.txt", 2) == 1
    assert _parse_id("70_question.txt", 2) == 70


def test_parse_id_wortfluessigkeit() -> None:
    assert _parse_id("0001_question.txt", 4) == 1
    assert _parse_id("1650_question.txt", 4) == 1650


def test_convert_figuren(tmp_path: Path) -> None:
    section_dir = tmp_path / "figuren"
    section_dir.mkdir()

    (section_dir / "001_question.txt").write_text(
        "Figuren zusammensetzen\nFrage 1\n", encoding="utf-8"
    )
    (section_dir / "001_solution.txt").write_text("C\n", encoding="utf-8")

    (section_dir / "002_question.txt").write_text(
        "Figuren zusammensetzen\nFrage 2\n", encoding="utf-8"
    )
    (section_dir / "002_solution.txt").write_text("A\n", encoding="utf-8")

    output_path = tmp_path / "questions.json"
    convert(tmp_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result["figuren"]) == 2
    assert result["figuren"][0]["id"] == 1
    assert result["figuren"][0]["answer"] == "C"
    assert result["figuren"][0]["content"] == "Figuren zusammensetzen\nFrage 1"
    assert result["figuren"][1]["id"] == 2
    assert result["figuren"][1]["answer"] == "A"


def test_convert_implikationen(tmp_path: Path) -> None:
    section_dir = tmp_path / "implikationen"
    section_dir.mkdir()

    (section_dir / "01_question.txt").write_text(
        "Prämissen:\n- Alle A sind B.\n\nA) X\nB) Y\nC) Z\nD) W\nE) Keine\n",
        encoding="utf-8",
    )
    (section_dir / "01_solution.txt").write_text("D\n", encoding="utf-8")

    output_path = tmp_path / "questions.json"
    convert(tmp_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result["implikationen"]) == 1
    assert result["implikationen"][0]["answer"] == "D"
    assert "Prämissen" in result["implikationen"][0]["content"]


def test_convert_wortfluessigkeit(tmp_path: Path) -> None:
    section_dir = tmp_path / "wortfluessigkeit"
    section_dir.mkdir()

    (section_dir / "0001_question.txt").write_text(
        "Buchstabenreihe: H U E A R E F\n\nA) U\nB) F\nC) E\nD) R\nE) Keine\n",
        encoding="utf-8",
    )
    (section_dir / "0001_solution.txt").write_text("C — EHEFRAU\n", encoding="utf-8")

    output_path = tmp_path / "questions.json"
    convert(tmp_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result["wortfluessigkeit"]) == 1
    assert result["wortfluessigkeit"][0]["answer"] == "C"


def test_convert_zahlenfolgen(tmp_path: Path) -> None:
    section_dir = tmp_path / "zahlenfolgen"
    section_dir.mkdir()

    (section_dir / "01_question.txt").write_text(
        "Zahlenfolge: 2 4 8 16 32 ?\n\nA) 33\nB) 48\nC) 64\nD) 128\nE) Keine\n",
        encoding="utf-8",
    )
    (section_dir / "01_solution.txt").write_text(
        "C — 64\nVerdopplung\n", encoding="utf-8"
    )

    output_path = tmp_path / "questions.json"
    convert(tmp_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result["zahlenfolgen"]) == 1
    assert result["zahlenfolgen"][0]["answer"] == "C"


def test_convert_ausweise(tmp_path: Path) -> None:
    cards_dir = tmp_path / "ausweise" / "cards"
    cards_dir.mkdir(parents=True)
    recall_dir = tmp_path / "ausweise" / "recall"
    recall_dir.mkdir(parents=True)

    (cards_dir / "001_question.txt").write_text(
        "Name: TEST\nGeburtstag: 1. Januar\nBlutgruppe: A\n", encoding="utf-8"
    )

    (recall_dir / "0001_question.txt").write_text(
        "Wie lautet der Name?\n\nA) X\nB) Y\nC) Z\nD) W\nE) Keine\n", encoding="utf-8"
    )
    (recall_dir / "0001_solution.txt").write_text("B\n", encoding="utf-8")

    output_path = tmp_path / "questions.json"
    convert(tmp_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result["ausweise_memorize"]) == 1
    assert result["ausweise_memorize"][0]["answer"] == ""
    assert "Name: TEST" in result["ausweise_memorize"][0]["content"]

    assert len(result["ausweise_recall"]) == 1
    assert result["ausweise_recall"][0]["answer"] == "B"


def test_convert_empty_section(tmp_path: Path) -> None:
    """Converter should skip sections that don't exist."""
    # Create only one section
    (tmp_path / "figuren").mkdir()
    (tmp_path / "figuren" / "001_question.txt").write_text("Test\n", encoding="utf-8")
    (tmp_path / "figuren" / "001_solution.txt").write_text("A\n", encoding="utf-8")

    output_path = tmp_path / "questions.json"
    convert(tmp_path, output_path)

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(result["figuren"]) == 1
    assert result["implikationen"] == []
    assert result["zahlenfolgen"] == []
    assert result["wortfluessigkeit"] == []

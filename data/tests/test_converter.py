from __future__ import annotations

from medat_parser.converter import generate_content


def test_figuren() -> None:
    content = generate_content("figuren", {"id": 7, "answer": "C"})
    assert "Figur 7" in content


def test_implikationen() -> None:
    data = {
        "id": 1,
        "premises": ["Alle A sind B.", "Kein B ist C."],
        "conclusions": {
            "A": "Alle A sind C.",
            "B": "Kein A ist C.",
            "C": "Einige A sind C.",
            "D": "Einige A sind nicht C.",
            "E": "Keine der Schlussfolgerungen ist richtig.",
        },
    }
    content = generate_content("implikationen", data)
    assert "Prämissen:" in content
    assert "- Alle A sind B." in content
    assert "- Kein B ist C." in content
    assert "A) Alle A sind C." in content
    assert "E) Keine der Schlussfolgerungen ist richtig." in content


def test_implikationen_empty_premises() -> None:
    data = {
        "id": 1,
        "premises": [],
        "conclusions": {"A": "X", "B": "Y", "C": "Z", "D": "W", "E": "Keine"},
    }
    content = generate_content("implikationen", data)
    assert "Prämissen:" in content
    assert "A) X" in content


def test_wortfluessigkeit() -> None:
    data = {
        "id": 1,
        "sequence": "H U E A R E F",
        "options": {
            "A": "U",
            "B": "F",
            "C": "E",
            "D": "R",
            "E": "Keine der Antworten ist richtig.",
        },
    }
    content = generate_content("wortfluessigkeit", data)
    assert "Buchstabenreihe:" in content
    assert "H U E A R E F" in content
    assert "A) U" in content
    assert "E) Keine der Antworten ist richtig." in content


def test_zahlenfolgen() -> None:
    data = {
        "id": 1,
        "sequence": "2 4 8 16 32 ?",
        "options": {
            "A": "33",
            "B": "48",
            "C": "64",
            "D": "128",
            "E": "Keine der Antworten ist richtig.",
        },
    }
    content = generate_content("zahlenfolgen", data)
    assert "Zahlenfolge:" in content
    assert "2 4 8 16 32 ?" in content
    assert "C) 64" in content


def test_unknown_section() -> None:
    try:
        generate_content("unknown", {"id": 1})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

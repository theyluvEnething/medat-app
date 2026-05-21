from __future__ import annotations

from medat_parser.utils import words_to_text


def test_empty() -> None:
    assert words_to_text([]) == ""


def test_single_line() -> None:
    words = [
        {"text": "Hello", "top": 10.0},
        {"text": "world", "top": 10.2},
    ]
    assert words_to_text(words) == "Hello world"


def test_multi_line() -> None:
    words = [
        {"text": "Line1", "top": 10.0},
        {"text": "Line2", "top": 22.0},
        {"text": "Line3", "top": 34.0},
    ]
    assert words_to_text(words) == "Line1\nLine2\nLine3"


def test_same_y_rounded() -> None:
    words = [
        {"text": "A", "top": 10.1},
        {"text": "B", "top": 10.4},
        {"text": "C", "top": 9.8},
    ]
    assert words_to_text(words) == "A B C"


def test_out_of_order_words() -> None:
    words = [
        {"text": "world", "top": 10.0},
        {"text": "Hello", "top": 10.0},
    ]
    result = words_to_text(words)
    assert "Hello" in result
    assert "world" in result

"""Parse Implikationen erkennen questions from PDF.

Two-column layout: questions 1-5 left, 6-10 right per page.
Answer key on the last page.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

from medat_parser.utils import words_to_text


def parse_implikationen(pdf_path: Path, output_dir: Path) -> None:
    pdf = pdfplumber.open(str(pdf_path))

    # Parse answers from last page
    answers: dict[int, str] = {}
    answer_text = pdf.pages[-1].extract_text()
    for match in re.finditer(r"(\d+)\.\s*([A-E])", answer_text):
        answers[int(match.group(1))] = match.group(2)

    # Question pages: index 1 to -2 (skip title page and answer page)
    question_pages = pdf.pages[1:-1]

    all_questions: list[dict] = []

    for page in question_pages:
        questions = _parse_page_columns(page, answers)
        all_questions.extend(questions)

    pdf.close()

    # Write output
    sets_dir = output_dir / "sets"
    sets_dir.mkdir(parents=True, exist_ok=True)

    for q in all_questions:
        set_dir = sets_dir / f"set_{q['set']:02d}"
        set_dir.mkdir(parents=True, exist_ok=True)
        q_file = set_dir / f"{q['id']:03d}.json"
        q_file.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")

    answers_file = output_dir / "answers.json"
    answers_file.write_text(
        json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Determine set count from max question id
    max_set = max(q["set"] for q in all_questions) if all_questions else 0
    print(f"Implikationen: {len(all_questions)} questions in {max_set} sets")


def _parse_page_columns(page, answers: dict[int, str]) -> list[dict]:
    """Split page into left/right columns and parse each column."""
    words = page.extract_words(keep_blank_chars=True)
    if not words:
        return []

    # Find column split: words with x0 < 200 are left column, >= 200 are right
    left_words = [w for w in words if w["x0"] < 200]
    right_words = [w for w in words if w["x0"] >= 200]

    questions: list[dict] = []

    for col_words in [left_words, right_words]:
        col_text = words_to_text(col_words)
        col_questions = _parse_column(col_text, answers)
        questions.extend(col_questions)

    return questions


def _parse_column(
    text: str, answers: dict[int, str]
) -> list[dict]:
    """Parse a single column of 5 questions. Question numbers are global (1-70)."""
    questions: list[dict] = []

    # Remove set header lines
    text = re.sub(r"^Übungsset\s+\d+\s*", "", text)

    # Split into question blocks by number pattern at line start
    blocks = re.split(r"\n(?=\d+\.\s)", text)

    for block in blocks:
        block = block.strip()
        m = re.match(r"(\d+)\.\s+(.*)", block, re.DOTALL)
        if not m:
            continue
        global_id = int(m.group(1))

        qtext = m.group(2).strip()
        lines = [l.strip() for l in qtext.split("\n") if l.strip()]

        premises: list[str] = []
        conclusions: dict[str, str] = {}
        for line in lines:
            cm = re.match(r"^([A-E])\.\s+(.*)", line)
            if cm:
                conclusions[cm.group(1)] = cm.group(2)
            else:
                premises.append(line)

        # Global numbering: questions 1-10 = set 1, 11-20 = set 2, etc.
        set_num = (global_id - 1) // 10 + 1
        set_index = (global_id - 1) % 10 + 1
        answer = answers.get(global_id, "")

        questions.append(
            {
                "id": global_id,
                "set": set_num,
                "set_index": set_index,
                "answer": answer,
                "premises": premises,
                "conclusions": conclusions,
            }
        )

    return questions


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse Implikationen erkennen PDF")
    parser.add_argument("--input", type=Path, required=True, help="Input PDF file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    parse_implikationen(args.input, args.output)


if __name__ == "__main__":
    main()

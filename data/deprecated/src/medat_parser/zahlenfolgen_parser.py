"""Parse Zahlenfolgen questions from PDF.

Single-column layout, 5 questions per page, 2 pages per set (10 questions).
Global numbering 1-70 across 7 sets.
Answer key has explanations.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


def parse_zahlenfolgen(pdf_path: Path, output_dir: Path) -> None:
    pdf = pdfplumber.open(str(pdf_path))

    # Find answer pages (contain "Lösungen" and "Zahlenfolgen")
    answer_start = None
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and "Lösungen" in text and "Zahlenfolgen" in text:
            answer_start = i
            break

    if answer_start is None:
        answer_start = len(pdf.pages) - 2

    # Parse answer key
    answers: dict[int, dict[str, str]] = {}
    for page in pdf.pages[answer_start:]:
        text = page.extract_text()
        # Pattern: "1. C 71/90 explanation..."
        for match in re.finditer(r"(\d+)\.\s+([A-E])\s+(\S+)\s+(.*?)(?=\n?\d+\.\s|\n?Set\s|\Z)", text, re.DOTALL):
            answers[int(match.group(1))] = {
                "letter": match.group(2),
                "value": match.group(3),
                "explanation": match.group(4).strip(),
            }

    # Parse questions (pages 1 to answer_start-1)
    all_questions: list[dict] = []
    for page in pdf.pages[1:answer_start]:
        text = page.extract_text()
        # Remove page number at the end
        text = re.sub(r"\n\d+\s*$", "", text.strip())
        # Remove set header
        text = re.sub(r"^\s*Übungsset\s+\d+\s*", "", text)

        questions = _parse_page(text, answers)
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

    max_set = max(q["set"] for q in all_questions) if all_questions else 0
    print(f"Zahlenfolgen: {len(all_questions)} questions in {max_set} sets")


def _parse_page(text: str, answers: dict[int, dict[str, str]]) -> list[dict]:
    """Parse a page with 5 single-column questions."""
    questions: list[dict] = []

    # Split by question numbers at line start: "N. "
    blocks = re.split(r"\n(?=\d+\.\s)", text)

    for block in blocks:
        block = block.strip()
        m = re.match(r"(\d+)\.\s+(.*)", block, re.DOTALL)
        if not m:
            continue
        global_id = int(m.group(1))
        if global_id > 70:
            continue

        qtext = m.group(2).strip()
        lines = [l.strip() for l in qtext.split("\n") if l.strip()]

        # First line is the number sequence
        sequence = lines[0] if lines else ""

        # Remaining lines are A-E options
        options: dict[str, str] = {}
        for line in lines[1:]:
            om = re.match(r"^([A-E])\.\s+(.*)", line)
            if om:
                options[om.group(1)] = om.group(2)

        answer_entry = answers.get(global_id, {})
        set_num = (global_id - 1) // 10 + 1
        set_index = (global_id - 1) % 10 + 1

        questions.append(
            {
                "id": global_id,
                "set": set_num,
                "set_index": set_index,
                "answer": answer_entry.get("letter", ""),
                "answer_value": answer_entry.get("value", ""),
                "explanation": answer_entry.get("explanation", ""),
                "sequence": sequence,
                "options": options,
            }
        )

    return questions


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse Zahlenfolgen PDF")
    parser.add_argument("--input", type=Path, required=True, help="Input PDF file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    parse_zahlenfolgen(args.input, args.output)


if __name__ == "__main__":
    main()

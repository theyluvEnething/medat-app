"""Parse Wortflüssigkeit questions from PDF.

150 pages of questions (2 columns × 5 questions each), 12 pages of answers.
Questions are globally numbered 1-1500, organized in 100 sets of 15.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

from medat_parser.utils import words_to_text


def parse_wortfluessigkeit(pdf_path: Path, output_dir: Path) -> None:
    pdf = pdfplumber.open(str(pdf_path))

    # Answer pages are at the end, starting from "Lösungen Wortflüssigkeit"
    answer_start = None
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and "Lösungen Wortflüssigkeit" in text:
            answer_start = i
            break

    if answer_start is None:
        answer_start = len(pdf.pages) - 12  # fallback

    # Parse answer key
    answers: dict[int, dict[str, str]] = {}
    for page in pdf.pages[answer_start:]:
        text = page.extract_text()
        for match in re.finditer(r"(\d+)\.\s+([A-E])\s+(\S+)", text):
            qid = int(match.group(1))
            answers[qid] = {
                "letter": match.group(2),
                "word": match.group(3),
            }

    # Parse questions from pages 1..answer_start-1
    all_questions: list[dict] = []
    question_pages = pdf.pages[1:answer_start]  # skip title page

    for page in question_pages:
        words = page.extract_words(keep_blank_chars=True)
        if not words:
            continue

        left_words = [w for w in words if w["x0"] < 250]
        right_words = [w for w in words if w["x0"] >= 250]

        for col_words in [left_words, right_words]:
            col_text = words_to_text(col_words)
            col_questions = _parse_column(col_text, answers)
            all_questions.extend(col_questions)

    pdf.close()

    # Write output
    sets_dir = output_dir / "sets"
    sets_dir.mkdir(parents=True, exist_ok=True)

    for q in all_questions:
        set_dir = sets_dir / f"set_{q['set']:03d}"
        set_dir.mkdir(parents=True, exist_ok=True)
        q_file = set_dir / f"{q['id']:04d}.json"
        q_file.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write answers index
    answers_file = output_dir / "answers.json"
    answers_file.write_text(
        json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    max_set = max(q["set"] for q in all_questions) if all_questions else 0
    print(f"Wortflüssigkeit: {len(all_questions)} questions in {max_set} sets")


def _parse_column(text: str, answers: dict[int, dict[str, str]]) -> list[dict]:
    """Parse a column of questions. Each question has a number, letter sequence, and A-E options."""
    questions: list[dict] = []

    # Remove set header line
    text = re.sub(r"^\s*Übungsset\s+\d+\s*", "", text)

    # Each question block starts with "N. " at line beginning
    # The options follow on subsequent lines as "A. X", "B. X", etc.
    lines = text.strip().split("\n")

    current_q: dict | None = None
    current_options: dict[str, str] = {}
    current_sequence = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is a question number line: "N. letters..."
        # Use search instead of match — stray chars may appear before the number
        qm = re.search(r"(\d+)\.\s+(.*)", line)
        if qm:
            # Save previous question
            if current_q is not None:
                current_q["options"] = current_options
                current_q["sequence"] = current_sequence.strip()
                questions.append(current_q)

            qid = int(qm.group(1))
            sequence = qm.group(2).strip()
            answer_entry = answers.get(qid, {})
            answer_letter = answer_entry.get("letter", "")
            answer_word = answer_entry.get("word", "")

            set_num = (qid - 1) // 15 + 1
            set_index = (qid - 1) % 15 + 1

            current_q = {
                "id": qid,
                "set": set_num,
                "set_index": set_index,
                "answer": answer_letter,
                "answer_word": answer_word,
            }
            current_options = {}
            current_sequence = sequence
            continue

        # Option line: "A. X" or "E. KeinederAntwortenistrichtig"
        om = re.match(r"^([A-E])\.\s+(.*)", line)
        if om and current_q is not None:
            current_options[om.group(1)] = om.group(2)
            continue

        # Continuation of sequence from previous line
        if current_q is not None and not om:
            current_sequence += " " + line

    # Save last question
    if current_q is not None:
        current_q["options"] = current_options
        current_q["sequence"] = current_sequence.strip()
        questions.append(current_q)

    return questions


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse Wortflüssigkeit PDF")
    parser.add_argument("--input", type=Path, required=True, help="Input PDF file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    parse_wortfluessigkeit(args.input, args.output)


if __name__ == "__main__":
    main()

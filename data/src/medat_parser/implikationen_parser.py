"""Parse Implikationen erkennen questions from PDF.

Two-column layout: questions 1-5 left, 6-10 right per page.
Answer key on the last page.

Output per question (flat directory):
  NN_question.txt  — premises + A–E conclusions
  NN_solution.txt  — answer letter
"""

from __future__ import annotations

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
    all_questions: list[dict] = []

    for page in pdf.pages[1:-1]:
        questions = _parse_page_columns(page, answers)
        all_questions.extend(questions)

    pdf.close()

    # Write flat output
    output_dir.mkdir(parents=True, exist_ok=True)

    for q in all_questions:
        qid = q["id"]

        # Question text
        premises = "\n".join(f"- {p}" for p in q["premises"])
        opts = "\n".join(
            f"{k}) {v}" for k, v in sorted(q["conclusions"].items())
        )
        question_text = f"Prämissen:\n{premises}\n\n{opts}\n"
        q_file = output_dir / f"{qid:02d}_question.txt"
        q_file.write_text(question_text, encoding="utf-8")

        # Solution text
        (output_dir / f"{qid:02d}_solution.txt").write_text(
            f"{q['answer']}\n", encoding="utf-8"
        )

    max_id = max(q["id"] for q in all_questions) if all_questions else 0
    print(f"Implikationen: {len(all_questions)} questions (IDs 1–{max_id})")


def _parse_page_columns(page, answers: dict[int, str]) -> list[dict]:
    """Split page into left/right columns and parse each column."""
    words = page.extract_words(keep_blank_chars=True)
    if not words:
        return []

    left_words = [w for w in words if w["x0"] < 200]
    right_words = [w for w in words if w["x0"] >= 200]

    questions: list[dict] = []
    for col_words in [left_words, right_words]:
        col_text = words_to_text(col_words)
        col_questions = _parse_column(col_text, answers)
        questions.extend(col_questions)

    return questions


def _parse_column(text: str, answers: dict[int, str]) -> list[dict]:
    """Parse a single column of 5 questions. Question numbers are global (1-70)."""
    questions: list[dict] = []

    text = re.sub(r"^Übungsset\s+\d+\s*", "", text)

    blocks = re.split(r"\n(?=\d+\.\s)", text)

    for block in blocks:
        block = block.strip()
        m = re.match(r"(\d+)\.\s+(.*)", block, re.DOTALL)
        if not m:
            continue
        global_id = int(m.group(1))

        qtext = m.group(2).strip()
        lines = [ln.strip() for ln in qtext.split("\n") if ln.strip()]

        premises: list[str] = []
        conclusions: dict[str, str] = {}
        for line in lines:
            cm = re.match(r"^([A-E])\.\s+(.*)", line)
            if cm:
                conclusions[cm.group(1)] = cm.group(2)
            else:
                premises.append(line)

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

    p = argparse.ArgumentParser(description="Parse Implikationen erkennen PDF")
    p.add_argument("--input", type=Path, required=True, help="Input PDF file")
    p.add_argument("--output", type=Path, required=True, help="Output directory")
    args = p.parse_args()

    parse_implikationen(args.input, args.output)


if __name__ == "__main__":
    main()

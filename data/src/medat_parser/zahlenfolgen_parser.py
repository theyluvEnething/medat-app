"""Parse Zahlenfolgen questions from PDF.

Single-column layout, 5 questions per page, 2 pages per set (10 questions).
Global numbering 1-70 across 7 sets.
Answer key has explanations.

Output per question (flat directory):
  NN_question.txt  — number sequence + A–E options
  NN_solution.txt  — answer letter + value + explanation
"""

from __future__ import annotations

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
        for match in re.finditer(
            r"(\d+)\.\s+([A-E])\s+(\S+)\s+(.*?)(?=\n?\d+\.\s|\n?Set\s|\Z)",
            text,
            re.DOTALL,
        ):
            answers[int(match.group(1))] = {
                "letter": match.group(2),
                "value": match.group(3),
                "explanation": match.group(4).strip(),
            }

    # Parse questions (pages 1 to answer_start-1)
    all_questions: list[dict] = []
    for page in pdf.pages[1:answer_start]:
        text = page.extract_text()
        text = re.sub(r"\n\d+\s*$", "", text.strip())
        text = re.sub(r"^\s*Übungsset\s+\d+\s*", "", text)

        questions = _parse_page(text, answers)
        all_questions.extend(questions)

    pdf.close()

    # Write flat output
    output_dir.mkdir(parents=True, exist_ok=True)

    for q in all_questions:
        qid = q["id"]

        # Question text
        opts = "\n".join(
            f"{k}) {v}" for k, v in sorted(q["options"].items())
        )
        question_text = f"Zahlenfolge: {q['sequence']}\n\n{opts}\n"
        q_file = output_dir / f"{qid:02d}_question.txt"
        q_file.write_text(question_text, encoding="utf-8")

        # Solution text
        answer_value = q.get("answer_value", "")
        explanation = q.get("explanation", "")
        lines = [f"{q['answer']} — {answer_value}"]
        if explanation:
            lines.append(explanation)
        (output_dir / f"{qid:02d}_solution.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    max_id = max(q["id"] for q in all_questions) if all_questions else 0
    print(f"Zahlenfolgen: {len(all_questions)} questions (IDs 1–{max_id})")


def _parse_page(text: str, answers: dict[int, dict[str, str]]) -> list[dict]:
    """Parse a page with 5 single-column questions."""
    questions: list[dict] = []

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
        lines = [ln.strip() for ln in qtext.split("\n") if ln.strip()]

        sequence = lines[0] if lines else ""

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

    p = argparse.ArgumentParser(description="Parse Zahlenfolgen PDF")
    p.add_argument("--input", type=Path, required=True, help="Input PDF file")
    p.add_argument("--output", type=Path, required=True, help="Output directory")
    args = p.parse_args()

    parse_zahlenfolgen(args.input, args.output)


if __name__ == "__main__":
    main()

"""Convert flat text output into the app's questions.json format.

Reads the flat output/<section>/ directory structure and produces a single
Record<section, Question[]> JSON file the Electron app imports at build time.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SECTION_KEYS = ["figuren", "zahlenfolgen", "wortfluessigkeit", "implikationen"]

ID_PAD = {
    "figuren": 3,
    "zahlenfolgen": 2,
    "wortfluessigkeit": 4,
    "implikationen": 2,
}


def _parse_id(filename: str, pad: int) -> int | None:
    m = re.match(rf"(\d{{{pad}}})_question\.txt", filename)
    return int(m.group(1)) if m else None


def _load_section(section_dir: Path, section_key: str) -> list[dict]:
    """Load all questions from a flat section directory."""
    pad = ID_PAD[section_key]
    questions: list[dict] = []

    for txt_file in sorted(section_dir.glob("*_question.txt")):
        qid = _parse_id(txt_file.name, pad)
        if qid is None:
            continue

        question_text = txt_file.read_text(encoding="utf-8").strip()

        sol_name = txt_file.name.replace("_question.txt", "_solution.txt")
        sol_file = section_dir / sol_name
        raw_sol = sol_file.read_text(encoding="utf-8") if sol_file.is_file() else ""
        solution_text = raw_sol.strip()

        # Extract answer letter from solution (first char before " — ")
        answer = ""
        if solution_text:
            answer = solution_text.split("\n")[0].split(" — ")[0].strip()

        questions.append(
            {
                "section": section_key,
                "id": qid,
                "answer": answer,
                "content": question_text,
            }
        )

    questions.sort(key=lambda q: q["id"])
    return questions


def _load_ausweise_cards(ausweise_dir: Path) -> list[dict]:
    """Load Ausweis cards from cards/ subdirectory."""
    cards_dir = ausweise_dir / "cards"
    if not cards_dir.is_dir():
        return []

    cards: list[dict] = []
    for txt_file in sorted(cards_dir.glob("*_question.txt")):
        m = re.match(r"(\d{3})_question\.txt", txt_file.name)
        if not m:
            continue
        qid = int(m.group(1))

        question_text = txt_file.read_text(encoding="utf-8").strip()

        img_file = cards_dir / f"{qid:03d}_question.png"
        image = f"{qid:03d}.png" if img_file.is_file() else ""

        cards.append(
            {
                "section": "ausweise_memorize",
                "id": qid,
                "answer": "",
                "content": question_text,
                "image": image,
            }
        )

    cards.sort(key=lambda c: c["id"])
    return cards


def _load_ausweise_recall(ausweise_dir: Path) -> list[dict]:
    """Load Ausweis recall questions from recall/ subdirectory."""
    recall_dir = ausweise_dir / "recall"
    if not recall_dir.is_dir():
        return []

    questions: list[dict] = []
    for txt_file in sorted(recall_dir.glob("*_question.txt")):
        m = re.match(r"(\d{4})_question\.txt", txt_file.name)
        if not m:
            continue
        qid = int(m.group(1))

        question_text = txt_file.read_text(encoding="utf-8").strip()

        sol_file = recall_dir / f"{qid:04d}_solution.txt"
        raw_sol = sol_file.read_text(encoding="utf-8") if sol_file.is_file() else ""
        solution_text = raw_sol.strip()

        answer = solution_text.split("\n")[0].strip() if solution_text else ""

        questions.append(
            {
                "section": "ausweise_recall",
                "id": qid,
                "answer": answer,
                "content": question_text,
            }
        )

    questions.sort(key=lambda q: q["id"])
    return questions


def convert(input_dir: Path, output_path: Path) -> None:
    """Read parser output and write combined questions.json."""
    result: dict[str, list[dict]] = {}

    for key in SECTION_KEYS:
        section_dir = input_dir / key
        questions = _load_section(section_dir, key) if section_dir.is_dir() else []
        result[key] = questions
        print(f"  {key}: {len(questions)} questions")

    # Ausweise: memorization cards + recall questions
    ausweise_dir = input_dir / "ausweise"
    if ausweise_dir.is_dir():
        memorize = _load_ausweise_cards(ausweise_dir)
        result["ausweise_memorize"] = memorize
        print(f"  ausweise_memorize: {len(memorize)} cards")

        recall = _load_ausweise_recall(ausweise_dir)
        result["ausweise_recall"] = recall
        print(f"  ausweise_recall: {len(recall)} questions")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(len(v) for v in result.values())
    print(f"Wrote {total} questions across {len(result)} sections to {output_path}")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Convert parsed MedAT data to app questions.json"
    )
    p.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Parser output directory (e.g. output/)",
    )
    p.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output questions.json path",
    )
    args = p.parse_args()
    convert(args.input, args.output)


if __name__ == "__main__":
    main()

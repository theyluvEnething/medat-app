"""Convert parsed MedAT question JSONs into the app's flat questions.json format.

Reads per-section parser output from output/<section>/sets/ and produces a single
Record<section, Question[]> JSON file the Electron app imports at build time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SECTION_KEYS = ["figuren", "zahlenfolgen", "wortfluessigkeit", "implikationen"]


def generate_content(section: str, data: dict) -> str:
    """Flatten a parsed question's rich fields into a single display string."""
    match section:
        case "figuren":
            return f"[Bild: Figur {data['id']}]"

        case "implikationen":
            premises = "\n".join(f"- {p}" for p in data.get("premises", []))
            conclusions = data.get("conclusions", {})
            options = "\n".join(
                f"{k}) {v}" for k, v in sorted(conclusions.items())
            )
            return f"Prämissen:\n{premises}\n\n{options}"

        case "wortfluessigkeit":
            seq = data.get("sequence", "")
            opts = data.get("options", {})
            options = "\n".join(
                f"{k}) {v}" for k, v in sorted(opts.items())
            )
            return f"Buchstabenreihe: {seq}\n\n{options}"

        case "zahlenfolgen":
            seq = data.get("sequence", "")
            opts = data.get("options", {})
            options = "\n".join(
                f"{k}) {v}" for k, v in sorted(opts.items())
            )
            return f"Zahlenfolge: {seq}\n\n{options}"

        case "ausweise_memorize":
            fields = data.get("fields", {})
            lines = [f"{key}: {value}" for key, value in fields.items()]
            return "\n".join(lines)

        case "ausweise_recall":
            text = data.get("text", "")
            opts = data.get("options", {})
            options = "\n".join(
                f"{k}) {v}" for k, v in sorted(opts.items())
            )
            return f"{text}\n\n{options}"

        case _:
            raise ValueError(f"Unknown section: {section}")


def load_section_questions(section_dir: Path, section_key: str) -> list[dict]:
    """Load all question JSONs from a section's output directory."""
    sets_dir = section_dir / "sets"
    if not sets_dir.is_dir():
        print(f"Warning: {sets_dir} not found, skipping {section_key}")
        return []

    questions: list[dict] = []
    for json_file in sorted(sets_dir.glob("set_*/*.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        questions.append(
            {
                "section": section_key,
                "id": data["id"],
                "answer": data.get("answer", ""),
                "content": generate_content(section_key, data),
            }
        )

    questions.sort(key=lambda q: q["id"])
    return questions


def convert(input_dir: Path, output_path: Path) -> None:
    """Read parser output and write combined questions.json."""
    result: dict[str, list[dict]] = {}

    for key in SECTION_KEYS:
        section_dir = input_dir / key
        questions = load_section_questions(section_dir, key)
        result[key] = questions
        print(f"  {key}: {len(questions)} questions")

    # Ausweise: memorization cards + recall questions
    ausweise_dir = input_dir / "ausweise"
    if ausweise_dir.is_dir():
        memorize = _load_ausweise_memorize(ausweise_dir)
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


def _load_ausweise_memorize(ausweise_dir: Path) -> list[dict]:
    """Load Ausweis cards into the memorize format (no answer, content=fields)."""
    sets_dir = ausweise_dir / "sets"
    if not sets_dir.is_dir():
        return []

    cards: list[dict] = []
    for json_file in sorted(sets_dir.glob("set_*/*.json")):
        if json_file.name.startswith("q_"):
            continue
        data = json.loads(json_file.read_text(encoding="utf-8"))
        cards.append(
            {
                "section": "ausweise_memorize",
                "id": data["id"],
                "answer": "",
                "content": generate_content("ausweise_memorize", data),
                "image": data.get("image", ""),
            }
        )
    cards.sort(key=lambda c: c["id"])
    return cards


def _load_ausweise_recall(ausweise_dir: Path) -> list[dict]:
    """Load Ausweis recall questions."""
    sets_dir = ausweise_dir / "sets"
    if not sets_dir.is_dir():
        return []

    questions: list[dict] = []
    for json_file in sorted(sets_dir.glob("set_*/q_*.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        questions.append(
            {
                "section": "ausweise_recall",
                "id": data["id"],
                "answer": data.get("answer", ""),
                "content": generate_content("ausweise_recall", data),
            }
        )
    questions.sort(key=lambda q: q["id"])
    return questions


def main() -> None:
    p = argparse.ArgumentParser(
        description="Convert parsed MedAT JSON to app questions.json"
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

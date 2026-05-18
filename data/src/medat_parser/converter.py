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


def load_ausweise(source_path: Path) -> dict[str, list[dict]]:
    """Extract ausweise_memorize and ausweise_recall from an existing questions.json."""
    if not source_path.is_file():
        print(f"Warning: {source_path} not found, Ausweise sections will be empty")
        return {}

    source = json.loads(source_path.read_text(encoding="utf-8"))
    result: dict[str, list[dict]] = {}
    for key in ("ausweise_memorize", "ausweise_recall"):
        if key in source:
            result[key] = source[key]
    return result


def convert(
    input_dir: Path, output_path: Path, ausweise_path: Path | None = None
) -> None:
    """Read parser output and write combined questions.json."""
    result: dict[str, list[dict]] = {}

    for key in SECTION_KEYS:
        section_dir = input_dir / key
        questions = load_section_questions(section_dir, key)
        result[key] = questions
        print(f"  {key}: {len(questions)} questions")

    if ausweise_path:
        ausweise = load_ausweise(ausweise_path)
        for key, questions in ausweise.items():
            result[key] = questions
            print(f"  {key}: {len(questions)} questions (from existing)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(len(v) for v in result.values())
    print(f"Wrote {total} questions across {len(result)} sections to {output_path}")


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
    p.add_argument(
        "--ausweise",
        type=Path,
        default=None,
        help="Existing questions.json to copy ausweise sections from",
    )
    args = p.parse_args()
    convert(args.input, args.output, args.ausweise)


if __name__ == "__main__":
    main()

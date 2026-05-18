"""Merge newly parsed PDF output into existing output with continuous indexing.

Parses new PDFs, remaps IDs/sets to continue from existing max values,
and merges into the real output directory.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _existing_maxes(output_dir: Path, section: str) -> tuple[int, int]:
    """Return (max_id, max_set) for existing output, or (0, 0) if none."""
    sets_dir = output_dir / section / "sets"
    if not sets_dir.is_dir():
        return 0, 0

    max_id = 0
    max_set = 0
    for json_file in sets_dir.glob("set_*/*.json"):
        if json_file.name.startswith("q_"):
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            max_id = max(max_id, data.get("id", 0))
            max_set = max(max_set, data.get("set", 0))
        except (json.JSONDecodeError, KeyError):
            pass
    return max_id, max_set


def remap_and_merge(
    temp_dir: Path,
    output_dir: Path,
    section: str,
    id_offset: int,
    set_offset: int,
    batch_label: str,
) -> int:
    """Remap IDs/sets in temp output and merge into real output.

    Returns the number of questions merged.
    """
    temp_section = temp_dir / section if (temp_dir / section).is_dir() else temp_dir
    temp_sets = temp_section / "sets"
    out_section = output_dir / section

    if not temp_sets.is_dir():
        print(f"  No sets found in {temp_sets}")
        return 0

    # Collect all question JSONs
    question_files = sorted(temp_sets.glob("set_*/*.json"))
    count = 0

    for src_file in question_files:
        if src_file.name.startswith("q_"):
            continue

        data = json.loads(src_file.read_text(encoding="utf-8"))
        old_id = data["id"]
        old_set = data["set"]

        new_id = id_offset + old_id
        new_set = set_offset + old_set

        data["id"] = new_id
        data["set"] = new_set

        # Remap solution_page for figuren
        if "solution_page" in data:
            data["solution_page"] = f"{batch_label}_{data['solution_page']}"

        # Determine output set directory
        set_fmt = "set_{:03d}" if section == "wortfluessigkeit" else "set_{:02d}"
        id_fmt = "{:04d}" if section == "wortfluessigkeit" else "{:03d}"

        out_set_dir = out_section / "sets" / set_fmt.format(new_set)
        out_set_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_set_dir / f"{id_fmt.format(new_id)}.json"
        _write_json(out_file, data)

        # Copy associated image (figuren: PNG in same set dir)
        if "image" in data:
            old_img = data["image"]
            new_img = f"{id_fmt.format(new_id)}.png"
            src_img = src_file.parent / old_img
            dst_img = out_set_dir / new_img
            if src_img.is_file():
                shutil.copy2(src_img, dst_img)
            data["image"] = new_img
            _write_json(out_file, data)

        count += 1

    # Merge answers
    temp_answers = temp_section / "answers.json"
    if temp_answers.is_file():
        existing_answers = {}
        out_answers = out_section / "answers.json"
        if out_answers.is_file():
            existing_answers = json.loads(out_answers.read_text(encoding="utf-8"))

        temp_data = json.loads(temp_answers.read_text(encoding="utf-8"))
        for old_key, value in temp_data.items():
            new_key = str(id_offset + int(old_key))
            existing_answers[new_key] = value

        _write_json(out_answers, existing_answers)

    # Copy solution images for figuren
    temp_solutions = temp_section / "solutions"
    if temp_solutions.is_dir():
        out_solutions = out_section / "solutions"
        out_solutions.mkdir(parents=True, exist_ok=True)
        for sol_file in temp_solutions.glob("*.png"):
            new_name = f"{batch_label}_{sol_file.name}"
            shutil.copy2(sol_file, out_solutions / new_name)

    return count


def merge_pdf(
    pdf_path: Path,
    section: str,
    parser_fn,
    output_dir: Path,
    used_dir: Path,
    batch_index: int,
) -> None:
    """Parse a PDF, remap IDs, merge into output, move PDF to .used/."""
    import tempfile

    print(f"Processing {pdf_path.name}...")

    # Parse to temp dir
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / section
        tmp_path.mkdir(parents=True, exist_ok=True)
        parser_fn(pdf_path, tmp_path)

        # Determine offsets
        max_id, max_set = _existing_maxes(output_dir, section)
        batch_label = f"batch{batch_index}"

        count = remap_and_merge(
            tmp_path, output_dir, section, max_id, max_set, batch_label
        )
        print(f"  Merged {count} questions (IDs {max_id + 1}-{max_id + count})")

    # Move PDF to .used/
    dest = used_dir / section / pdf_path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(pdf_path), str(dest))
    print(f"  Moved to {dest}")


def main() -> None:
    import argparse

    from medat_parser.figuren_parser import parse_figuren
    from medat_parser.wortfluessigkeit_parser import parse_wortfluessigkeit

    section_parsers = {
        "figuren": parse_figuren,
        "wortfluessigkeit": parse_wortfluessigkeit,
    }

    p = argparse.ArgumentParser(description="Merge new PDFs into existing output")
    p.add_argument("--input", type=Path, required=True, help="input/ directory")
    p.add_argument("--output", type=Path, required=True, help="output/ directory")
    p.add_argument(
        "--section",
        type=str,
        choices=list(section_parsers),
        help="Section to process (default: all that have new PDFs)",
    )
    args = p.parse_args()

    input_dir = args.input
    output_dir = args.output
    used_dir = input_dir / ".used"

    sections_to_process = (
        [args.section] if args.section else list(section_parsers)
    )

    for section in sections_to_process:
        section_input = input_dir / section
        if not section_input.is_dir():
            continue

        pdf_files = sorted(section_input.glob("*.pdf"))
        if not pdf_files:
            continue

        # Determine starting batch index from .used/ count + 1
        section_used = used_dir / section
        existing = (
            len(list(section_used.glob("*.pdf"))) if section_used.is_dir() else 0
        )
        batch_index = existing + 1

        parser_fn = section_parsers[section]

        for pdf_path in pdf_files:
            merge_pdf(
                pdf_path, section, parser_fn, output_dir, used_dir, batch_index
            )
            batch_index += 1


if __name__ == "__main__":
    main()

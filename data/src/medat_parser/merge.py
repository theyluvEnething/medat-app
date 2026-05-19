"""Merge newly parsed PDF output into existing output with continuous indexing.

Parses new PDFs, remaps IDs to continue from existing max values,
and merges into the real output directory.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ID_PAD = {
    "figuren": 3,
    "zahlenfolgen": 2,
    "wortfluessigkeit": 4,
    "implikationen": 2,
}


def _existing_max_id(output_dir: Path, section: str, sub: str | None = None) -> int:
    """Return the highest question ID in the existing output directory."""
    target = output_dir / section
    if sub:
        target = target / sub

    if not target.is_dir():
        return 0

    max_id = 0
    for f in target.glob("*_question.txt"):
        m = re.match(r"(\d+)_question\.txt", f.name)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return max_id


def _remap_and_copy(
    temp_dir: Path, output_dir: Path, section: str, id_offset: int
) -> int:
    """Copy files from temp to output, remapping IDs by id_offset.

    Returns the number of questions merged.
    """
    count = 0

    # Determine pattern for this section
    if section == "ausweise":
        count += _remap_ausweise(temp_dir, output_dir, id_offset)
        return count

    pad = ID_PAD.get(section, 3)
    target_dir = output_dir / section
    target_dir.mkdir(parents=True, exist_ok=True)

    # Find question files in temp
    temp_section = temp_dir / section
    for txt_file in sorted(temp_section.glob("*_question.txt")):
        m = re.match(r"(\d+)_question\.txt", txt_file.name)
        if not m:
            continue
        old_id = int(m.group(1))
        new_id = id_offset + old_id

        # Copy and rename question text
        new_name = f"{new_id:0{pad}d}_question.txt"
        shutil.copy2(str(txt_file), str(target_dir / new_name))

        # Copy and rename solution text
        sol_name = txt_file.name.replace("_question.txt", "_solution.txt")
        old_sol = temp_section / sol_name
        if old_sol.is_file():
            new_sol_name = f"{new_id:0{pad}d}_solution.txt"
            shutil.copy2(str(old_sol), str(target_dir / new_sol_name))

        # Copy and rename images
        for ext in [".png"]:
            img_name = txt_file.name.replace("_question.txt", f"_question{ext}")
            old_img = temp_section / img_name
            if old_img.is_file():
                new_img_name = f"{new_id:0{pad}d}_question{ext}"
                shutil.copy2(str(old_img), str(target_dir / new_img_name))

        count += 1

    # Copy solution pages for figuren
    temp_solutions = temp_section / "solutions"
    if temp_solutions.is_dir():
        out_solutions = target_dir / "solutions"
        out_solutions.mkdir(parents=True, exist_ok=True)
        for sol_file in temp_solutions.glob("*.png"):
            if not (out_solutions / sol_file.name).exists():
                shutil.copy2(str(sol_file), str(out_solutions / sol_file.name))

    return count


def _remap_ausweise(temp_dir: Path, output_dir: Path, id_offset: int) -> int:
    """Remap and merge Ausweise cards and recall questions."""
    count = 0
    temp_ausweise = temp_dir / "ausweise"

    # Cards
    temp_cards = temp_ausweise / "cards"
    if temp_cards.is_dir():
        cards_dir = output_dir / "ausweise" / "cards"
        cards_dir.mkdir(parents=True, exist_ok=True)

        max_card = _existing_max_id(output_dir, "ausweise", "cards")
        for txt_file in sorted(temp_cards.glob("*_question.txt")):
            m = re.match(r"(\d+)_question\.txt", txt_file.name)
            if not m:
                continue
            old_id = int(m.group(1))
            new_id = max_card + old_id

            new_name = f"{new_id:03d}_question.txt"
            shutil.copy2(str(txt_file), str(cards_dir / new_name))

            old_img = temp_cards / f"{old_id:03d}_question.png"
            if old_img.is_file():
                new_img = cards_dir / f"{new_id:03d}_question.png"
                shutil.copy2(str(old_img), str(new_img))

            count += 1

    # Recall questions
    temp_recall = temp_ausweise / "recall"
    if temp_recall.is_dir():
        recall_dir = output_dir / "ausweise" / "recall"
        recall_dir.mkdir(parents=True, exist_ok=True)

        max_recall = _existing_max_id(output_dir, "ausweise", "recall")
        for txt_file in sorted(temp_recall.glob("*_question.txt")):
            m = re.match(r"(\d+)_question\.txt", txt_file.name)
            if not m:
                continue
            old_id = int(m.group(1))
            new_id = max_recall + old_id

            new_name = f"{new_id:04d}_question.txt"
            shutil.copy2(str(txt_file), str(recall_dir / new_name))

            old_sol = temp_recall / f"{old_id:04d}_solution.txt"
            if old_sol.is_file():
                new_sol = recall_dir / f"{new_id:04d}_solution.txt"
                shutil.copy2(str(old_sol), str(new_sol))

            count += 1

    return count


def merge_pdf(
    pdf_path: Path,
    section: str,
    parser_fn,
    output_dir: Path,
    used_dir: Path,
) -> None:
    """Parse a PDF, remap IDs, merge into output, move PDF to .used/."""
    import tempfile

    print(f"Processing {pdf_path.name}...")

    # Compute ID offset from existing output
    id_offset = _existing_max_id(output_dir, section)
    if section == "ausweise":
        id_offset = _existing_max_id(output_dir, section, "cards")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / section
        tmp_path.mkdir(parents=True, exist_ok=True)
        parser_fn(pdf_path, tmp_path)

        count = _remap_and_copy(Path(tmp), output_dir, section, id_offset)
        print(f"  Merged {count} items (offset {id_offset})")

    dest = used_dir / section / pdf_path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(pdf_path), str(dest))
    print(f"  Moved to {dest}")


def main() -> None:
    import argparse

    from medat_parser.ausweise_parser import parse_ausweise
    from medat_parser.figuren_parser import parse_figuren
    from medat_parser.implikationen_parser import parse_implikationen
    from medat_parser.wortfluessigkeit_parser import parse_wortfluessigkeit
    from medat_parser.zahlenfolgen_parser import parse_zahlenfolgen

    section_parsers = {
        "figuren": parse_figuren,
        "wortfluessigkeit": parse_wortfluessigkeit,
        "implikationen": parse_implikationen,
        "zahlenfolgen": parse_zahlenfolgen,
        "ausweise": parse_ausweise,
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

        parser_fn = section_parsers[section]

        for pdf_path in pdf_files:
            merge_pdf(pdf_path, section, parser_fn, output_dir, used_dir)


if __name__ == "__main__":
    main()

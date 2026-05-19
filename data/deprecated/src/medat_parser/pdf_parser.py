"""Extract MedAT KFF questions from PDF exercise books.

Unified entry point that dispatches to per-section parsers.
Expects input directory layout: input/<section>/*.pdf
"""

from __future__ import annotations

import argparse
from pathlib import Path

from medat_parser.ausweise_parser import parse_ausweise
from medat_parser.figuren_parser import parse_figuren
from medat_parser.implikationen_parser import parse_implikationen
from medat_parser.wortfluessigkeit_parser import parse_wortfluessigkeit
from medat_parser.zahlenfolgen_parser import parse_zahlenfolgen

PARSERS = {
    "figuren": ("Figuren zusammensetzen", parse_figuren),
    "wortfluessigkeit": ("Wortflüssigkeit", parse_wortfluessigkeit),
    "implikationen": ("Implikationen erkennen", parse_implikationen),
    "zahlenfolgen": ("Zahlenfolgen", parse_zahlenfolgen),
    "ausweise": ("Ausweise Merken", parse_ausweise),
}


def parse_all(input_base: Path, output_dir: Path) -> None:
    """Run all parsers on PDFs found in input_base/<section>/ directories."""
    for key, (label, parser_fn) in PARSERS.items():
        section_input = input_base / key
        pdf_files = list(section_input.glob("*.pdf")) if section_input.is_dir() else []

        if not pdf_files:
            print(f"Warning: No PDF found in {section_input}")
            continue

        pdf_path = pdf_files[0]
        if len(pdf_files) > 1:
            print(f"Note: Multiple PDFs in {section_input}, using {pdf_path.name}")

        section_dir = output_dir / key
        section_dir.mkdir(parents=True, exist_ok=True)
        print(f"Parsing {label} from {pdf_path.name}...")
        parser_fn(pdf_path, section_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract MedAT questions from PDFs")
    parser.add_argument(
        "--input", type=Path, required=True, help="PDF file or input/ directory"
    )
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--section",
        type=str,
        choices=list(PARSERS) + ["all"],
        default="all",
        help="Section to parse (default: all)",
    )
    args = parser.parse_args()

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.section == "all":
        if args.input.is_dir():
            parse_all(args.input, output_dir)
        else:
            print("Single file mode: trying all parsers...")
            for key, (_label, parser_fn) in PARSERS.items():
                section_dir = output_dir / key
                section_dir.mkdir(parents=True, exist_ok=True)
                try:
                    parser_fn(args.input, section_dir)
                except Exception as e:
                    print(f"  {key}: failed — {e}")
    else:
        _label, parser_fn = PARSERS[args.section]
        section_dir = output_dir / args.section
        section_dir.mkdir(parents=True, exist_ok=True)
        parser_fn(args.input, section_dir)


if __name__ == "__main__":
    main()

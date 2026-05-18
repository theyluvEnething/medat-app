"""Extract MedAT KFF questions from PDF exercise books.

Unified entry point that dispatches to per-section parsers.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from medat_parser.figuren_parser import parse_figuren
from medat_parser.implikationen_parser import parse_implikationen
from medat_parser.wortfluessigkeit_parser import parse_wortfluessigkeit
from medat_parser.zahlenfolgen_parser import parse_zahlenfolgen

PARSERS = {
    "figuren": ("Figuren zusammensetzen", parse_figuren, "Figuren zusammensetzen"),
    "wortfluessigkeit": ("Wortflüssigkeit", parse_wortfluessigkeit, "Wortflüssigkeit"),
    "implikationen": ("Implikationen erkennen", parse_implikationen, "Implikationen erkennen"),
    "zahlenfolgen": ("Zahlenfolgen", parse_zahlenfolgen, "Zahlenfolgen"),
}


def parse_all(pdf_dir: Path, output_dir: Path) -> None:
    """Run all parsers on PDFs found in pdf_dir."""
    pdf_files = {p.stem: p for p in pdf_dir.glob("*.pdf")}

    for key, (_label, parser_fn, pdf_hint) in PARSERS.items():
        # Find matching PDF by name hint
        match = None
        for stem, path in pdf_files.items():
            if pdf_hint.lower().startswith(stem.lower()[:8]):
                match = path
                break

        if match is None:
            # Try fuzzy match
            for stem, path in pdf_files.items():
                if pdf_hint.lower()[:6] in stem.lower():
                    match = path
                    break

        if match is None:
            print(f"Warning: No PDF found for {pdf_hint}")
            continue

        section_dir = output_dir / key
        section_dir.mkdir(parents=True, exist_ok=True)
        print(f"Parsing {pdf_hint} from {match.name}...")
        parser_fn(match, section_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract MedAT questions from PDFs")
    parser.add_argument("--input", type=Path, required=True, help="PDF file or directory")
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
            # Single PDF: try to guess section from filename
            # For single file mode, run all parsers against the same file
            print("Single file mode: trying all parsers...")
            for key, (_label, parser_fn, _hint) in PARSERS.items():
                section_dir = output_dir / key
                section_dir.mkdir(parents=True, exist_ok=True)
                try:
                    parser_fn(args.input, section_dir)
                except Exception as e:
                    print(f"  {key}: failed — {e}")
    else:
        _label, parser_fn, _hint = PARSERS[args.section]
        section_dir = output_dir / args.section
        section_dir.mkdir(parents=True, exist_ok=True)
        parser_fn(args.input, section_dir)


if __name__ == "__main__":
    main()

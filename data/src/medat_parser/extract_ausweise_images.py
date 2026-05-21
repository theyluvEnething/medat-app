"""Extract question images from Ausweise Merken recall pages.

Some recall questions show a face photo from an allergy pass and ask
e.g. "What is the name of this person?". This script renders each recall
question page and crops individual question blocks so the app can display
the embedded image alongside the question text.

Output: output/ausweise/recall/NNNN_question.png (alongside existing .txt files)
"""

from __future__ import annotations

from pathlib import Path

import fitz
import pdfplumber
from PIL import Image

RENDER_DPI = 200
LEFT_X0 = 40
COL_SPLIT = 290
RIGHT_X1 = 550
TOP_MARGIN = 5
GAP_MARGIN = 5


def extract_images(pdf_path: Path, output_dir: Path) -> None:
    recall_dir = output_dir / "ausweise" / "recall"
    recall_dir.mkdir(parents=True, exist_ok=True)

    pdf = pdfplumber.open(str(pdf_path))
    fitz_doc = fitz.open(str(pdf_path))
    total_pages = len(pdf.pages)

    # Classify pages (same logic as ausweise_parser)
    ausweis_pages: set[int] = set()
    answer_start = None

    for i in range(total_pages):
        text = pdf.pages[i].extract_text() or ""
        if not text.strip():
            continue
        first_line = text.strip().split("\n")[0]
        if "Name:" in first_line:
            ausweis_pages.add(i)
        elif i > 2 and not answer_start and "Lösungen" in text:
            answer_start = i

    question_pages = []
    for i in range(2, answer_start if answer_start else total_pages):
        text = pdf.pages[i].extract_text() or ""
        if not text.strip():
            continue
        first_line = text.strip().split("\n")[0].strip()
        if (
            i not in ausweis_pages
            and not first_line.startswith("Übungsset")
            and not first_line.startswith("bungsset")
        ):
            question_pages.append(i)

    scale = RENDER_DPI / 72.0
    skipped = 0
    extracted = 0

    for page_idx in question_pages:
        page = pdf.pages[page_idx]
        words = page.extract_words(keep_blank_chars=True)
        if not words:
            skipped += 1
            continue

        # Find question numbers and their y-positions (split by column)
        left_numbers: list[tuple[int, float]] = []   # (qid, top)
        right_numbers: list[tuple[int, float]] = []

        for w in words:
            t = w["text"].strip()
            if t.endswith(".") and t[:-1].isdigit():
                num = int(t[:-1])
                if 1 <= num <= 1000:
                    if w["x0"] < COL_SPLIT:
                        left_numbers.append((num, w["top"]))
                    else:
                        right_numbers.append((num, w["top"]))

        # Sort each column by y-position (top to bottom)
        left_numbers.sort(key=lambda x: x[1])
        right_numbers.sort(key=lambda x: x[1])

        if not left_numbers and not right_numbers:
            skipped += 1
            continue

        # Render page
        fitz_page = fitz_doc[page_idx]
        pix = fitz_page.get_pixmap(dpi=RENDER_DPI)
        page_png_path = recall_dir / f"_page_{page_idx:03d}.png"
        pix.save(str(page_png_path))
        full_img = Image.open(str(page_png_path))

        page_bottom = full_img.height

        # Crop questions from each column
        for col_items, col_x0, col_x1 in [
            (left_numbers, LEFT_X0, COL_SPLIT),
            (right_numbers, COL_SPLIT, RIGHT_X1),
        ]:
            for i, (qid, qtop_pt) in enumerate(col_items):
                y0 = max(0, int(qtop_pt * scale) - int(TOP_MARGIN * scale))

                if i < len(col_items) - 1:
                    _, next_top = col_items[i + 1]
                    y1 = int(next_top * scale) - int(GAP_MARGIN * scale)
                else:
                    y1 = page_bottom - int(TOP_MARGIN * scale)

                y1 = min(page_bottom, y1)

                if y1 <= y0:
                    continue

                x0_px = int(col_x0 * scale)
                x1_px = int(col_x1 * scale)

                cropped = full_img.crop((x0_px, y0, x1_px, y1))
                img_path = recall_dir / f"{qid:04d}_question.png"
                cropped.save(str(img_path))
                cropped.close()
                extracted += 1

        full_img.close()
        page_png_path.unlink()

    pdf.close()
    fitz_doc.close()

    print(f"Ausweise recall images: {extracted} extracted, {skipped} pages skipped")


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="Extract question images from Ausweise recall pages"
    )
    p.add_argument("--input", type=Path, required=True, help="Ausweise PDF file")
    p.add_argument("--output", type=Path, required=True, help="Output root (e.g. output/)")
    args = p.parse_args()

    extract_images(args.input, args.output)


if __name__ == "__main__":
    main()

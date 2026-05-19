"""Parse Figuren zusammensetzen questions from PDF.

Each page has exactly 3 figuren as vector graphics. We render pages
with PyMuPDF and split each page into 3 equal-height question images.
Answer key is parsed from the last 4 pages, which we also render as
full-page solution images.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

RENDER_DPI = 200


def parse_figuren(pdf_path: Path, output_dir: Path) -> None:
    pdf = pdfplumber.open(str(pdf_path))

    # Find answer start page ("Lösungen" + "Figuren zusammensetzen")
    answer_start = None
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and "Lösungen" in text and "Figuren zusammensetzen" in text:
            answer_start = i
            break

    if answer_start is None:
        answer_start = len(pdf.pages) - 4

    # Parse answer key from text pages
    answers: dict[int, str] = {}
    for page in pdf.pages[answer_start:]:
        text = page.extract_text()
        for match in re.finditer(r"(\d+)\.\s*([A-E])(?=[\s,]|$)", text):
            answers[int(match.group(1))] = match.group(2)

    # Parse question positions for splitting
    question_pages = list(range(1, answer_start))  # 0-indexed page indices
    all_questions: list[dict] = []

    for page_idx in question_pages:
        page = pdf.pages[page_idx]
        words = page.extract_words(keep_blank_chars=True)

        # Find question numbers and their y-positions
        q_items: list[tuple[int, float, float]] = []  # (qnum, top, bottom)
        for w in words:
            text = w["text"].strip()
            if text.endswith(".") and text[:-1].isdigit():
                num = int(text[:-1])
                if 1 <= num <= 105:
                    q_items.append((num, w["top"], w["bottom"]))

        q_items.sort(key=lambda x: x[0])

        if len(q_items) < 3:
            continue

        # Compute split points: each question from its number to next question's number
        questions_in_page = []
        for i, (qnum, qtop, _qbottom) in enumerate(q_items):
            if i < len(q_items) - 1:
                # Bottom is just above the next question number
                _, next_top, _ = q_items[i + 1]
                question_bottom = next_top - 5  # 5pt margin
            else:
                # Last question: go to page bottom minus margin
                question_bottom = page.height - 10

            questions_in_page.append(
                {
                    "qnum": qnum,
                    "top": qtop,
                    "bottom": question_bottom,
                }
            )

        all_questions.append((page_idx, questions_in_page))

    pdf.close()

    # Now render pages and split using PyMuPDF
    fitz_doc = fitz.open(str(pdf_path))

    sets_dir = output_dir / "sets"
    sets_dir.mkdir(parents=True, exist_ok=True)
    solutions_dir = output_dir / "solutions"
    solutions_dir.mkdir(parents=True, exist_ok=True)

    # Render solution pages
    for sol_page_idx in range(answer_start, len(fitz_doc)):
        sol_page = fitz_doc[sol_page_idx]
        pix = sol_page.get_pixmap(dpi=RENDER_DPI)
        sol_file = solutions_dir / f"page_{sol_page_idx + 1:02d}.png"
        pix.save(str(sol_file))

    # Render question pages and split
    for page_idx, q_items in all_questions:
        fitz_page = fitz_doc[page_idx]
        pix = fitz_page.get_pixmap(dpi=RENDER_DPI)
        page_png_path = output_dir / f"_page_{page_idx:02d}.png"
        pix.save(str(page_png_path))

        scale = RENDER_DPI / 72.0  # points to pixels

        for q in q_items:
            global_id = q["qnum"]
            set_num = (global_id - 1) // 15 + 1
            set_index = (global_id - 1) % 15 + 1

            # Map set to solution page (some sets span multiple solution pages)
            _sol_map = {1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 3, 7: 3}
            sol_offset = _sol_map.get(set_num, 0)
            sol_page = answer_start + sol_offset

            # Crop region in pixels
            y0 = int(q["top"] * scale)
            y1 = int(q["bottom"] * scale)
            # Clamp to pixmap bounds
            y0 = max(0, y0)
            y1 = min(pix.height, y1)

            # Save cropped question image
            set_dir = sets_dir / f"set_{set_num:02d}"
            set_dir.mkdir(parents=True, exist_ok=True)
            img_file = f"{global_id:03d}.png"

            # Use Pillow to crop
            from PIL import Image

            full_img = Image.open(str(page_png_path))
            cropped = full_img.crop((0, y0, full_img.width, y1))
            cropped.save(str(set_dir / img_file))
            full_img.close()

            answer = answers.get(global_id, "")

            q_json = {
                "id": global_id,
                "set": set_num,
                "set_index": set_index,
                "answer": answer,
                "image": img_file,
                "solution_page": f"page_{sol_page + 1:02d}.png",
            }
            (set_dir / f"{global_id:03d}.json").write_text(
                json.dumps(q_json, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        # Clean up temp page image
        page_png_path.unlink()

    fitz_doc.close()

    # Write answers index
    answers_file = output_dir / "answers.json"
    answers_file.write_text(
        json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total = sum(1 for _ in output_dir.rglob("*.json") if _.parent.name.startswith("set"))
    max_set = max(
        int(p.parent.name.split("_")[1])
        for p in output_dir.rglob("*.json")
        if p.parent.name.startswith("set")
    )
    print(f"Figuren: {total} questions in {max_set} sets")
    print(f"Solutions: {len(list(solutions_dir.iterdir()))} pages")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse Figuren zusammensetzen PDF")
    parser.add_argument("--input", type=Path, required=True, help="Input PDF file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    parse_figuren(args.input, args.output)


if __name__ == "__main__":
    main()

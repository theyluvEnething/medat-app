"""Parse Ausweise Merken (Allergy Pass) questions from PDF.

Each of the 40 sets has:
- 4 pages with 2 Ausweise each = 8 Ausweise per set
- 3 pages with 25 recall questions (2-column layout, interleaved)
- Answer key at the very back of the PDF (pages 322-325)

Each Ausweis is rendered as a cropped PNG image and its text fields are parsed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import fitz
import pdfplumber
from PIL import Image

from medat_parser.utils import words_to_text

AUSWEIS_FIELDS = [
    "Name",
    "Geburtstag",
    "Medikamenteneinnahme",
    "Blutgruppe",
    "Bekannte Allergien",
    "Ausweisnummer",
    "Ausstellungsland",
]

# Crop bounds for the two Ausweise on a page (in points, at 200 DPI)
# page dimensions: 595.28 x 841.89 pt
_TOP_CROP = (15, 70, 580, 440)
_BOTTOM_CROP = (15, 430, 580, 800)
_DPI = 200


def _pt_to_px(pt: float) -> int:
    return round(pt * _DPI / 72)


def parse_ausweise(pdf_path: Path, output_dir: Path) -> None:
    pdf = pdfplumber.open(str(pdf_path))
    total_pages = len(pdf.pages)

    # Open PyMuPDF for image rendering
    fitz_doc = fitz.open(str(pdf_path))

    # Classify pages
    ausweis_pages: list[int] = []
    question_pages: list[int] = []
    answer_start = None

    for i in range(total_pages):
        text = pdf.pages[i].extract_text() or ""
        if not text.strip():
            continue

        first_line = text.strip().split("\n")[0]

        if "Name:" in first_line:
            ausweis_pages.append(i)
        elif i > 2 and not answer_start and "Lösungen" in text:
            answer_start = i

    # Questions are pages that aren't the title, image, set headers,
    # Ausweise, or answers. Set headers contain "Übungsset N".
    for i in range(2, answer_start if answer_start else total_pages):
        text = pdf.pages[i].extract_text() or ""
        if not text.strip():
            continue
        first_line = text.strip().split("\n")[0].strip()
        if (
            "Name:" not in first_line
            and not first_line.startswith("Übungsset")
            and not first_line.startswith("bungsset")
        ):
            question_pages.append(i)

    # Parse answers
    answers: dict[int, str] = {}
    if answer_start:
        for i in range(answer_start, total_pages):
            text = pdf.pages[i].extract_text() or ""
            for match in re.finditer(r"(\d+)\.\s+([A-E])", text):
                answers[int(match.group(1))] = match.group(2)

    # Parse Ausweise
    ausweise: list[dict] = []
    ausweis_id = 0

    sets_dir = output_dir / "sets"
    sets_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for page_num in ausweis_pages:
        page = pdf.pages[page_num]
        words = page.extract_words(keep_blank_chars=True)

        # Render page at 200 DPI for image cropping
        fitz_page = fitz_doc[page_num]
        pix = fitz_page.get_pixmap(dpi=_DPI)
        full_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # Split into top and bottom Ausweise
        top_words = [w for w in words if w["top"] < 430]
        bottom_words = [w for w in words if w["top"] >= 430]

        for _idx, (half_words, crop_bounds) in enumerate(
            [(top_words, _TOP_CROP), (bottom_words, _BOTTOM_CROP)]
        ):
            if not half_words:
                continue

            ausweis_id += 1
            fields = _parse_ausweis_fields(half_words)

            set_num = (ausweis_id - 1) // 8 + 1
            set_index = (ausweis_id - 1) % 8 + 1

            # Crop and save image
            crop_px = tuple(_pt_to_px(v) for v in crop_bounds)
            cropped = full_img.crop(crop_px)
            image_filename = f"{ausweis_id:03d}.png"
            cropped.save(str(images_dir / image_filename), "PNG")

            entry = {
                "id": ausweis_id,
                "set": set_num,
                "set_index": set_index,
                "image": image_filename,
                "fields": fields,
            }
            ausweise.append(entry)

            # Write individual Ausweis JSON
            set_dir = sets_dir / f"set_{set_num:02d}"
            set_dir.mkdir(parents=True, exist_ok=True)
            json_path = set_dir / f"{ausweis_id:03d}.json"
            json_path.write_text(
                json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    # Parse questions
    all_questions: list[dict] = []
    for page_num in question_pages:
        page = pdf.pages[page_num]
        words = page.extract_words(keep_blank_chars=True)
        if not words:
            continue

        left_words = [w for w in words if w["x0"] < 290]
        right_words = [w for w in words if w["x0"] >= 290]

        for col_words in [left_words, right_words]:
            col_text = words_to_text(col_words)
            col_questions = _parse_question_column(col_text, answers)
            all_questions.extend(col_questions)

    # Write questions
    for q in all_questions:
        set_dir = sets_dir / f"set_{q['set']:02d}"
        set_dir.mkdir(parents=True, exist_ok=True)
        q_file = set_dir / f"q_{q['id']:04d}.json"
        q_file.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write answers index
    answers_file = output_dir / "answers.json"
    answers_file.write_text(
        json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    pdf.close()
    fitz_doc.close()

    print(
        f"Ausweise Merken: {len(ausweise)} Ausweise, "
        f"{len(all_questions)} questions across "
        f"{max((q['set'] for q in all_questions), default=0)} sets"
    )


def _parse_ausweis_fields(words: list) -> dict[str, str]:
    """Extract labeled fields from Ausweis word objects."""
    text = words_to_text(words)
    lines = text.split("\n")
    fields: dict[str, str] = {}

    for line in lines:
        for field in AUSWEIS_FIELDS:
            if line.startswith(field):
                value = line[len(field):].strip().lstrip(":").strip()
                fields[field] = value
                break

    return fields


def _parse_question_column(
    text: str, answers: dict[int, str]
) -> list[dict]:
    """Parse a column of recall questions into structured dicts."""
    questions: list[dict] = []
    lines = text.strip().split("\n")

    current_q: dict | None = None
    current_text_lines: list[str] = []
    current_options: dict[str, str] = {}
    in_options = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        qm = re.match(r"(\d+)\.\s+(.*)", line)
        if qm:
            if current_q is not None:
                current_q["text"] = " ".join(current_text_lines)
                current_q["options"] = current_options
                questions.append(current_q)

            qid = int(qm.group(1))
            set_num = (qid - 1) // 25 + 1
            set_index = (qid - 1) % 25 + 1
            answer = answers.get(qid, "")

            current_q = {
                "id": qid,
                "set": set_num,
                "set_index": set_index,
                "answer": answer,
            }
            current_text_lines = [qm.group(2).strip()]
            current_options = {}
            in_options = False
            continue

        om = re.match(r"^([A-E])\.\s+(.*)", line)
        if om and current_q is not None:
            current_options[om.group(1)] = om.group(2)
            in_options = True
            continue

        if current_q is not None and not in_options:
            current_text_lines.append(line)

    if current_q is not None:
        current_q["text"] = " ".join(current_text_lines)
        current_q["options"] = current_options
        questions.append(current_q)

    return questions


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse Ausweise Merken PDF")
    parser.add_argument("--input", type=Path, required=True, help="Input PDF file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    parse_ausweise(args.input, args.output)


if __name__ == "__main__":
    main()

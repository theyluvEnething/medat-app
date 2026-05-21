"""Generate synthetic Implikationen erkennen exercises.

Produces flat NN_question.txt + NN_solution.txt files that merge seamlessly
with parsed PDF output. IDs continue from the highest existing ID.

Usage: uv run medat-generate-implikationen --count 1000
"""

from __future__ import annotations

import random
from pathlib import Path

# ── Statement types (Premise 1: A→B, Premise 2: B→C) ──────────────────────

STATEMENTS = [
    ("Alle {A} sind {B}.", "{A} ⊂ {B}"),
    ("Alle {A} sind keine {B}.", "{A} ∩ {B} = ∅"),
    ("Einige {A} sind {B}.", "{A} ∩ {B} ≠ ∅"),
    ("Einige {A} sind keine {B}.", "{A} ⊄ {B}"),
]

# ── Answer templates (index 0-3: concrete conclusions, 4: "none correct") ─

CONCLUSION_TEMPLATES = [
    "Alle {A} sind {C}.",
    "Alle {A} sind keine {C}.",
    "Einige {A} sind {C}.",
    "Einige {A} sind keine {C}.",
    "Keine der Schlussfolgerungen ist richtig.",
]

# ── Rule matrix: (premise1_idx, premise2_idx) → conclusion_idx ────────────
# Indices: 0=All-in, 1=All-none, 2=Some-in, 3=Some-none, 4=None-correct

RULE_SET: dict[tuple[int, int], int] = {
    (0, 0): 0,  # All A are B  +  All B are C      → All A are C
    (0, 1): 1,  # All A are B  +  All B are no C    → All A are no C
    (0, 2): 2,  # All A are B  +  Some B are C      → Some A are C
    (0, 3): 4,  # All A are B  +  Some B are no C   → none
    (1, 0): 1,  # All A no B   +  All B are C       → All A are no C
    (1, 1): 4,  # All A no B   +  All B are no C    → none
    (1, 2): 4,  # All A no B   +  Some B are C      → none
    (1, 3): 4,  # All A no B   +  Some B are no C   → none
    (2, 0): 2,  # Some A are B +  All B are C       → Some A are C
    (2, 1): 3,  # Some A are B +  All B are no C    → Some A are no C
    (2, 2): 4,  # Some A are B +  Some B are C      → none
    (2, 3): 4,  # Some A are B +  Some B are no C   → none
    (3, 0): 4,  # Some A no B  +  All B are C       → none
    (3, 1): 4,  # Some A no B  +  All B are no C    → none
    (3, 2): 4,  # Some A no B  +  Some B are C      → none
    (3, 3): 4,  # Some A no B  +  Some B are no C   → none
}

# ── Noun pool for A / B / C categories ────────────────────────────────────

NOUNS = [
    "Ärzte", "Amseln", "Amphibien", "Anwälte", "Autos",
    "Bäume", "Blumen", "Bücher", "Chemiker", "Delfine",
    "Diamanten", "Dichter", "Dinosaurier", "Eichen", "Eidechsen",
    "Elektroautos", "Fische", "Flugzeuge", "Flüsse", "Fotografen",
    "Gedichte", "Gemälde", "Giraffen", "Glühbirnen", "Granite",
    "Gräser", "Haie", "Häuser", "Hunde", "Insekten",
    "Ingenieure", "Kätzchen", "Klaviere", "Krokodile", "Kupfer",
    "Lehrer", "Lilien", "Maler", "Mammute", "Marder",
    "Mathematiker", "Mäuse", "Menschen", "Metalle", "Möbel",
    "Musikinstrumente", "Nashörner", "Orchideen", "Pandas", "Pilze",
    "Politiker", "Quallen", "Quartette", "Radios", "Reptilien",
    "Roboter", "Rosen", "Sänger", "Säugetiere", "Schauspieler",
    "Schiffe", "Schlangen", "Schriftsteller", "Skulpturen", "Smartphones",
    "Spatzen", "Sportler", "Statuen", "Stühle", "Tabletten",
    "Tannen", "Taucher", "Telefone", "Teleskope", "Tiger",
    "Tomaten", "Tulpen", "Türen", "Uhren", "Vasen",
    "Vegetarier", "Vögel", "Vulkane", "Wale", "Werkzeuge",
    "Wirbeltiere", "Wissenschaftler", "Wölfe", "Zebras", "Züge",
]


def _pick_nouns() -> tuple[str, str, str]:
    """Return three distinct random nouns for A, B, C."""
    return tuple(random.sample(NOUNS, 3))  # type: ignore[return-value]


def generate_one(seed: int | None = None) -> dict:
    """Generate a single Implikationen exercise.

    Returns a dict with keys: premises, conclusion_idx, options (shuffled),
    answer_letter, answer_text.
    """
    if seed is not None:
        random.seed(seed)

    p1_idx = random.randrange(4)
    p2_idx = random.randrange(4)
    conclusion_idx = RULE_SET[(p1_idx, p2_idx)]

    a_name, b_name, c_name = _pick_nouns()

    premise1 = STATEMENTS[p1_idx][0].format(A=a_name, B=b_name)
    premise2 = STATEMENTS[p2_idx][0].format(A=b_name, B=c_name)

    # Build the 4 concrete conclusion options
    concrete = [
        CONCLUSION_TEMPLATES[i].format(A=a_name, C=c_name) for i in range(4)
    ]

    # Shuffle first 4; option E is always "Keine der Schlussfolgerungen ist richtig."
    indices = list(range(4))
    random.shuffle(indices)
    shuffled_options = [concrete[i] for i in indices] + [CONCLUSION_TEMPLATES[4]]

    # Find where the correct answer landed
    answer_position = 4 if conclusion_idx == 4 else indices.index(conclusion_idx)

    answer_letter = ["A", "B", "C", "D", "E"][answer_position]

    return {
        "premise1": premise1,
        "premise2": premise2,
        "premise_types": (p1_idx, p2_idx),
        "conclusion_idx": conclusion_idx,
        "options": shuffled_options,
        "answer_letter": answer_letter,
        "answer_text": shuffled_options[answer_position],
    }


def format_question(ex: dict) -> str:
    """Format a generated exercise as a question text block."""
    lines = ["Prämissen:"]
    lines.append(f"- {ex['premise1']}")
    lines.append(f"- {ex['premise2']}")
    lines.append("")
    for i, opt in enumerate(ex["options"]):
        letter = ["A", "B", "C", "D", "E"][i]
        lines.append(f"{letter}) {opt}")
    return "\n".join(lines)


def format_solution(ex: dict) -> str:
    """Format the solution text."""
    return f"{ex['answer_letter']}\n"


def generate_set(count: int, output_dir: Path, start_id: int = 1) -> int:
    """Generate `count` exercises into output_dir with sequential IDs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        qid = start_id + i
        ex = generate_one(seed=qid)

        q_text = format_question(ex)
        s_text = format_solution(ex)

        (output_dir / f"{qid:04d}_question.txt").write_text(q_text + "\n", encoding="utf-8")
        (output_dir / f"{qid:04d}_solution.txt").write_text(s_text, encoding="utf-8")

    return start_id + count - 1


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="Generate synthetic Implikationen erkennen exercises"
    )
    p.add_argument("--count", type=int, default=1000, help="Number of exercises")
    p.add_argument("--output", type=Path, required=True, help="Output directory")
    p.add_argument(
        "--start-id", type=int, default=1, help="First question ID (default: 1)"
    )
    args = p.parse_args()

    last_id = generate_set(args.count, args.output, args.start_id)
    print(
        f"Implikationen: {args.count} exercises generated "
        f"(IDs {args.start_id}–{last_id})"
    )


if __name__ == "__main__":
    main()
